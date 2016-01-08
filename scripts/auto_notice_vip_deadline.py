#!/usr/bin/env python
#coding: utf8
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, notice, models  
import datetime 
import time 

reply = u'''
[VIP会员过期通知]

尊敬的用户，很抱歉的通知您的【疯狂人脉说】VIP会员已过期，VIP特权已取消，同时您的二维码海报也失效了( ˇˍˇ )。在此疯狂人脉说感谢您的支持,同时也希望您继续成为VIP，让我们更好的为您效劳：）重新购买vip -> http://v.fkduobao.com/sc/shop/buy
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

def getVipOutOfServices():
    all_vip_users = models.FansQueue.objects() 
    out_of_services_users = [] 
    now = time.mktime(datetime.datetime.now().timetuple())  
    for user in all_vip_users:
        user_vip_deadline = time.mktime(user.user.vip_deadline.timetuple()) 
        if user_vip_deadline <= now:
            out_of_services_users.append(user.user) 
    return out_of_services_users 

if __name__ == '__main__':
    with app.app_context():
        #users = get2rdSpreadUsers() 
        #users = getBaiyangUser() 
        #users = getAllUsers() 
        #users = getLatestUsers() 
        users = getVipOutOfServices() 
        sendTips(users) 
        #sendTipsMoney(users) 
