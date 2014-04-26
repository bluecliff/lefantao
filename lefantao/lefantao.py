#!/usr/bin/env python
# encoding: utf-8
from flask import render_template,make_response,request
from flask.views import MethodView
import xml.etree.ElementTree as ET
import time
from utils import get_items,add_user

EventKeyNo={
        u'TODAY_ITEMS':0,
        u'3C':1,
        u'BEAUTY':2,
        u'FOOD':3,
        u'HOMELIVE':4,
        u'MORE':12,
        }


def get_context(dom):
        context={}
        context['myName'] = dom.find('ToUserName').text
        context['toName'] = dom.find('FromUserName').text
        context['createTime'] = int(time.time())
        return context

def subscribeHandler(dom):
    """处理订阅事件"""
    fromname = dom.find('FromUserName').text
    add_user(fromname)
    context=get_context(dom)
    context['content']=u"欢迎您订阅乐翻淘，我们将为您提供各种高性价比的购物推荐。现在您可以回复对应的编号查询最新的网购促销信息"
    return render_template('erro.html',**context)

def clickHandler(dom):
    """处理菜单点击事件"""
    cate = dom.find('EventKey').text
    context=get_context(dom)
    if 0<=EventKeyNo[cate]<=11:
        context['items']=get_items(EventKeyNo[cate])
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
            context['items']=get_items(int(content))
            return render_template('show_items.html',**context)
        else:
            context["content"]=u"回复对应的编号可查询最新的相关网购促销信息:"
            return render_template('erro.html',**context)

class Lefantao(MethodView):
    msgHandler={
            u'event':MessageHandler.eventMessageHandler,
            u'text':MessageHandler.textMessageHandler,
            }
    def get(self):
        """处理合法请求认证"""
        string = request.args.get('echostr', '')
        return make_response(string)
    def post(self):
        """处理消息相应"""
        data = request.stream.read()
        dom=ET.fromstring(data)
        msgtype = dom.find('MsgType').text
        return self.msgHandler[msgtype](dom)
