#!/usr/bin/env python
#coding: utf8
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, notice, models  
import datetime 

reply = u'''
亲 请问有什么可以帮到你的呢？ 我们的平台可以上传二维码，让百万人加你微信，同时还可以赚钱哟  
''' 

def sendTips(users):
    for i in users:
        print '%s VIP消息已经下发...' % i 
        notice.send_text(i, u'VIP消息下发', reply) 

def sendTipsMoney(users):
    global reply 
    for i in users:
        nickname = i.nickname
        left_money = i.getCommission()   
        print "%s 佣金提现通知..." % i 
        print reply 
        reply = reply % (nickname, left_money)  
        notice.send_text(i, u'佣金提现通知', reply) 

def getNonVipUsers():
    nonVipUsers = [] 
    users = models.User.objects() 
    for i in users:
        if not i.isVip():
            nonVipUsers.append(i)  
    
    return nonVipUsers 

def get2rdSpreadUsers():
    users = models.User.objects(commission__gt=0) 
    return users 

def getBaiyangUser():
    return models.User.objects(openid="obmdTw4eo6ACVP5W8zvYyyhpuODA") 

def getAllUsers():
    return models.User.objects() 

def getLatestUsers():
    now = datetime.datetime.now().date() - datetime.timedelta(days=2)  
    return models.User.objects(update_info_time__gte=now) 

if __name__ == '__main__':
    with app.app_context():
        #users = get2rdSpreadUsers() 
        #users = getBaiyangUser() 
        #users = getAllUsers() 
        users = getLatestUsers() 
        sendTips(users) 
        #sendTipsMoney(users) 
