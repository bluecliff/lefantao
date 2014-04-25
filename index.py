#encoding: utf-8

from flask import Flask,request,g,render_template,make_response
from flask.views import MethodView
import MySQLdb
import xml.etree.ElementTree as ET
import time
import urllib
import json
from bae.core.wsgi import WSGIApplication


#HOST="127.0.0.1"
#USER="root"
#PASSWORD="jsfli"
#DBNAME="lefangou"
CHARSET="utf8"

#dbname = "mytest"
dbname = "uBwCaFPOHivuJfvjeygo"
categories={
'3834':[1,'数码家电'],
'3876':[2,'个护化妆'],
'6616':[3,'食品保健'],
'3877':[4,'家居生活'],
'3983':[5,'图书音像'],
'3873':[6,'服饰鞋包'],
'3880':[7,'母婴玩具'],
'3883':[8,'钟表首饰'],
'18301':[9,'运动户外'],
'8609':[10,'杂七杂八'],
'99999':[11,'其它']
}

app = Flask(__name__)


EventKeyNo={
        u'TODAY_ITEMS':0,
        u'3C':1,
        u'BEAUTY':2,
        u'FOOD':3,
        u'HOMELIVE':4,
        u'MORE':12,
        }

class MessageHandler(object):
    @classmethod
    def get_context(cls,dom):
        context={}
        context['myName'] = dom.find('ToUserName').text
        context['toName'] = dom.find('FromUserName').text
        context['createTime'] = int(time.time())
        return context
    @classmethod
    def subscribeHandler(cls,dom):
        """处理订阅事件"""
        fromname = dom.find('FromUserName').text
        addNewUser(fromname)
        context=cls.get_context(dom)
        context['content']="欢迎您订阅乐翻淘，我们将为您提供各种高性价比的购物推荐。现在您可以回复对应的编号查询最新的网购促销信息"
        return render_template('erro.html',**context)

    @classmethod
    def clickHandler(cls,dom):
        """处理菜单点击事件"""
        cate = dom.find('Event').text
        context=cls.get_context(dom)
        if 0<=EventKeyNo[cate]<=11:
            context['items']=getItems(EventKeyNo[cate])
            return render_template('show_items.html',**context)
        else:
            context["content"]="回复对应的编号可查询最新的相关网购促销信息:"
            return render_template('erro.html',**context)

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
        context=cls.get_context(dom)
        content = dom.find('Content').text
        if not content.isdigit():
            if content==u'是':
                context['content']="感谢您的参与，敬请期待新功能上线～～"
                return render_template('welcome.html',**context)
            elif content==u'否':
                context["content"]="感谢您的参与，谢谢~~"
                return render_template('welcome.html',**context)
            else:
                context["content"]="回复对应的编号可查询最新的相关网购促销信息:"
                return render_template('erro.html',**context)
        if 0<=int(content)<=11:
            context['items']=getItems(int(content))
            return render_template('show_items.html',**context)
        else:
            context["content"]="回复对应的编号可查询最新的相关网购促销信息:"
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
        self.msgHandler[msgtype]


def connect_db():
    return MySQLdb.connect(host = 'sqld.duapp.com',port = 4050,user ='nQEFKnIlEoYbdP2TrNOAseE6',passwd ='mk3BABDi7pGEsA1lewFyIqpIZzfhj72F' ,db = dbname,charset='utf8')


@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()


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

def send_items(cate_id,myname,fromname):
    createTime=int(time.time())
    if cate_id>11:
        contents={"content":"回复对应的编号可查询最新的相关网购促销信息:",'time':createTime,'myname':myname.encode('utf-8'),'fromname':fromname.encode('utf-8')}
        return render_template('erro.html',contents=contents)
    items=getItems(cate_id)
    return render_template('show_items.html',time=createTime, myname = myname, fromname=fromname,items=items)


def insert_item(item,cursor):
    cate_list=item[u'msg_categories'].split(u',')
    cate_id=11
    for cate in cate_list:
        if categories.has_key(cate.encode('utf-8')):
            cate_id=categories[cate.encode('utf-8')][0]
            break

    msg_id=item[u'msg_id']
    query="SELECT * FROM items where item_msg_id=%s" %(msg_id)
    n=cursor.execute(query)
    if n!=0:
        return "not insert"
    sql="INSERT INTO items (item_name,item_url,item_img,item_desc,item_cate_id,item_msg_id) VALUES('%s','%s','%s','%s',%s,%s)" %(item[u'msg_title'].encode('utf-8'),item[u'msg_buyurl'].encode('utf-8'),item[u'msg_picurl'].encode('utf-8'),item[u'msg_desc'].encode('utf-8'),cate_id,msg_id)
    n=cursor.execute(sql)
    return str(n)

@app.route('/pullItem/')
def pullItem():
    #db=connect_db()
    cursor=g.db.cursor()
    #cursor.execute("SET NAMES utf8")
    #g.db.commit()
    time_now=int(time.time())
    time_last=time_now-3000000
    url="http://www.smzdm.com/api_mobile/1.php?f=browser&mod=get_post_twenty&time=%s&lasttime=%s" %(time_now,time_last)

    res=json.loads(urllib.urlopen(url).read())
    if res.has_key(u'data'):
        for item in res[u'data']:
            insert_item(item,cursor)
    return "OK"

lft_view=Lefantao.as_view('lft')
app.add_url_rule('/wx/',view_func=lft_view,methods=['GET','POST'])
application = WSGIApplication(app)

if __name__ == '__main__':
    lft_view=Lefantao.as_view('lft')
    app.add_url_rule('/wx/',view_func=lft_view,methods=['GET','POST'])
    app.debug=True
    app.run()
