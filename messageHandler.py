#!/usr/bin/env python
# encoding: utf-8
from flask import g,render_template
import time

EventKeyNo={
        u'TODAY_ITEMS':0,
        u'3C':1,
        u'BEAUTY':2,
        u'FOOD':3,
        u'HOMELIVE':4,
        u'MORE':12,
        }

def getItems(m):
    cursor=g.db.cursor()
    sql = ''
    if m==0:
        sql='select item_name, item_url, item_img, item_desc, item_time from items order by item_id desc limit 10'
    else:
        sql='select item_name, item_url, item_img, item_desc, item_time from items where item_cate_id = %s order by item_id desc limit 8' % m

    n = cursor.execute(sql)
    items=[]
    for row in cursor.fetchall():
        items.append({'item_name':row[0],'item_url':row[1],'item_img':row[2],'item_desc':row[3]})
    cursor.close()
    return items

def addNewUser(username):
    cursor=g.db.cursor()
    sql="insert into subscriptions(cate_id,user_name) values(0,'%s')" %(username)
    n = cursor.execute(sql)
    cursor.close()
    return str(n)


def get_context(dom):
        context={}
        context['myName'] = dom.find('ToUserName').text
        context['toName'] = dom.find('FromUserName').text
        context['createTime'] = int(time.time())
        return context

def subscribeHandler(dom):
    """处理订阅事件"""
    fromname = dom.find('FromUserName').text
    addNewUser(fromname)
    context=get_context(dom)
    context['content']=u"欢迎您订阅乐翻淘，我们将为您提供各种高性价比的购物推荐。现在您可以回复对应的编号查询最新的网购促销信息"
    return render_template('erro.html',**context)

def clickHandler(dom):
    """处理菜单点击事件"""
    cate = dom.find('EventKey').text
    context=get_context(dom)
    if 0<=EventKeyNo[cate]<=11:
        context['items']=getItems(EventKeyNo[cate])
        return render_template('show_items.html',**context)
    else:
        context["content"]=u"回复对应的编号可查询最新的相关网购促销信息:"
        return render_template('erro.html',**context)


class MessageHandler(object):
    eventHandler={
            u'subscribe':subscribeHandler,
            u'CLICK':clickHandler
            }
    @classmethod
    def eventMessageHandler(cls,dom):
        """处理even事件"""
        eventtype = dom.find('Event').text
        return cls.eventHandler[eventtype](dom)
    @classmethod
    def textMessageHandler(cls,dom):
        """处理text事件"""
        context=get_context(dom)
        content = dom.find('Content').text
        if not content.isdigit():
            if content==u'是':
                context['content']=u"感谢您的参与，敬请期待新功能上线～～"
                return render_template('welcome.html',**context)
            elif content==u'否':
                context["content"]=u"感谢您的参与，谢谢~~"
                return render_template('welcome.html',**context)
            else:
                context["content"]=u"回复对应的编号可查询最新的相关网购促销信息:"
                return render_template('erro.html',**context)
        if 0<=int(content)<=11:
            context['items']=getItems(int(content))
            return render_template('show_items.html',**context)
        else:
            context["content"]=u"回复对应的编号可查询最新的相关网购促销信息:"
            return render_template('erro.html',**context)
