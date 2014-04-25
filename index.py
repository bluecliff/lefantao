#encoding: utf-8

from flask import Flask,request,g,render_template,make_response
from flask.views import MethodView
import MySQLdb
import xml.etree.ElementTree as ET
import time
import urllib
import json
from messageHandler import MessageHandler
#from bae.core.wsgi import WSGIApplication


HOST="127.0.0.1"
PORT=3306
USER="root"
PASSWORD="jsfli"
DBNAME="uBwCaFPOHivuJfvjeygo"
CHARSET="utf8"

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


def connect_db():
    return MySQLdb.connect(host = HOST,port = PORT,user =USER,passwd =PASSWORD,db = DBNAME,charset=CHARSET)


@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

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
#application = WSGIApplication(app)

if __name__ == '__main__':
#    lft_view=Lefantao.as_view('lft')
#    app.add_url_rule('/wx/',view_func=lft_view,methods=['GET','POST'])
    app.debug=True
    app.run()
