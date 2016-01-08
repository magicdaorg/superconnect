#coding: utf8
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime

import time
import json
from app import models, notice  
from app import app as appinstance
import config 

def newUserNotice(user, add_time):
    '''需要延迟10s发放''' 
    now = datetime.datetime.now() 
    delta = now - add_time
    if delta.seconds < 15:
        return False  

    upline_user = user.promo_upline
    if upline_user.isVirtualUser():
        return True 

    msg = u'''
            您好，[%s]刚刚成为您的1级人脉，恭喜您哟!\n<a href="%s/sc/ucenter/list/1?fr=menu">点击查看</a>  
           ''' % (user.nickname, config.SuperConnect.DOMAIN)  
    notice.send_text(upline_user, u'新下线', msg)  
    return True 

def newUserHandler():
    break_flag = False
    while True:
        if break_flag:
            continue
        new_users = models.NewUserQueue.objects() 
        if new_users.count() <= 0:
            print "Sleep 5s..." 
            time.sleep(5) 

        for u in new_users:
            '''新用户提醒'''
            ret = newUserNotice(u.user, u.add_time) 
            if ret:
                u.delete() 
if __name__ == '__main__':
    newUserHandler() 
