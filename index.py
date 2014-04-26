#encoding: utf-8

from flask import Flask
from lefantao.lefantao import Lefantao
from lefantao.grab import grab_items
from apscheduler.scheduler import Scheduler
import logging
#from bae.core.wsgi import WSGIApplication

app = Flask(__name__)



lft_view=Lefantao.as_view('lft')
app.add_url_rule('/wx/',view_func=lft_view,methods=['GET','POST'])
#application = WSGIApplication(app)

if __name__ == '__main__':
    logging.basicConfig(filename='lefantao.log',level=logging.INFO)
    sched=Scheduler()
    sched.start()
    sched.add_cron_job(grab_items,second=20)
    app.debug=True
    app.run()
