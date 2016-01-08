#coding: utf8
from flask import url_for
if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime
import traceback
import json
from app import app, models 


URL_PREFIX = '%s' % app.config['DOMAIN']

def buyOk(user, first, order, remark=u''):
    '''订单支付成功通知'''
    reply = u'''
    [订单支付成功]
    Hi, 亲爱的, 你已经成为VIP会员. 接下来你要做二件事哟!\n 
    1. 上传二维码, 让更多的人加你, <a href="http://v.fkduobao.com/sc/ucenter/upload">点击上传</a>二维码.\n 
    2. 分享疯狂人脉说二维码给你的朋友, 赚钱!!! 同行中最高佣金提成, 高达30%. 同时，你分享的次数越多，在粉丝人脉中的排名也会靠前哟, 请记住这很重要. 靠的越前, 加好友的人越多. <a href="http://mp.weixin.qq.com/s?__biz=MzI3NzAyMzA4Ng==&mid=211656975&idx=2&sn=3b26a4c1bb0776793e7d1e51eeb5cdf0#rd">点击</a>了解详情.\n 
''' 
    send_text(user, u'购买成功', reply) 

def userNewCommission(user, origin_user, fee, commission):
    '''用户新佣金通知'''
    reply = u'''
    [新佣金通知]
    Hi, 您好!\n
    您有一笔来自您的人脉[%s]的提成，订单总额为%s元，其中您提成为%s元. <a href="%s/sc/ucenter/money?fr=menu">点击</a>请查看
''' % (origin_user, fee, commission, URL_PREFIX) 
    models.TipsLog(user=user, send_type="weixin", content_type="text", tip_type=u'新佣金', data=reply, delay_time=0).save() 

def send_text(user, tip_type, text, delay_time=0):
    models.TipsLog(user=user, send_type="weixin", content_type="text", tip_type=tip_type, data=text, delay_time=delay_time).save()  

def redpack_sent_notice(user, number):
    reply = u'''
    [佣金提现成功通知]\n  
    Hi, 您好！\n    您提取的疯狂人脉说 [%s] 积分已经发放，请到[微信]-[我]-[钱包]零钱进行查看, 或者查看平台提现记录，<a href="%s/sc/ucenter/wallet?fr=menu">点击查看</a>  
''' % (number, URL_PREFIX) 
    models.TipsLog(user=user, send_type="weixin", content_type="text", tip_type=u'提现', data=reply, delay_time=0).save()  

def send_subcribe_commission(user, number):
    reply = u'''
    [感谢关注] 
    Hi，您好! \n    您有1分钱入账哟！分享自己的推广二维码，能得到更多积分(积分可以提现)，<a href="%s">点击生成</a>推广自己的二维码 
''' % 'http://v.fkduobao.com/sc/promotion/qrcode/%s?fr=subscribe' % user.id  
    models.TipsLog(user=user, send_type="weixin", content_type="text", tip_type=u'主动关注佣金', data=reply, delay_time=0).save()  

if __name__ == '__main__':
    with app.app_context():
        user = models.User.objects(openid="obmdTw4eo6ACVP5W8zvYyyhpuODA").first()  
        order = models.Order.objects(pay_id="H201508221440231498").first() 
        buyOk(user, '', order, '') 
