#!/usr/bin/env python
# encoding: utf-8

import MySQLdb
from config import*


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



def connect_db():
    return MySQLdb.connect(host = HOST,port = PORT,user =USER,passwd =PASSWORD,db = DBNAME,charset=CHARSET)

def close_db(db):
    db.close()

def get_items(m):
    db=connect_db()
    cursor=db.cursor()
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
    close_db(db)
    return items

def add_user(username):
    db=connect_db()
    cursor=db.cursor()
    sql="insert into subscriptions(cate_id,user_name) values(0,'%s')" %(username)
    n = cursor.execute(sql)
    cursor.close()
    return str(n)

def add_items(items):
    db=connect_db()
    cursor=db.cursor()
    count=0
    for item in items:
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
            continue
        sql="INSERT INTO items (item_name,item_url,item_img,item_desc,item_cate_id,item_msg_id) VALUES('%s','%s','%s','%s',%s,%s)" %(item[u'msg_title'].encode('utf-8'),item[u'msg_buyurl'].encode('utf-8'),item[u'msg_picurl'].encode('utf-8'),item[u'msg_desc'].encode('utf-8'),cate_id,msg_id)
        n=cursor.execute(sql)
        count+=n
    cursor.close()
    close_db(db)
    return count

