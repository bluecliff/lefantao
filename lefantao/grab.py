#!/usr/bin/env python
# encoding: utf-8
import time
import urllib
import json
from utils import add_items
import logging

def grab_items():
    time_now=int(time.time())
    time_last=time_now-3000000
    url="http://www.smzdm.com/api_mobile/1.php?f=browser&mod=get_post_twenty&time=%s&lasttime=%s" %(time_now,time_last)

    res=json.loads(urllib.urlopen(url).read())
    if res.has_key(u'data'):
        n = add_items(res[u'data'])
        logging.info("add %s items into db, %s",str(n),time.asctime())
    else:
        logging.info("Nothing to grab,%s",time.asctime())
