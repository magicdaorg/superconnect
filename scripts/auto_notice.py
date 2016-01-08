#coding: utf8
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime

from app import models 
import time 
import json 
import traceback 
from app import app as appinstance
import socket 
socket.setdefaulttimeout(10) 

def send_weixin_notice(x):
    openid = x['to']
    data = {
        'touser': openid,
        'template_id': x['template_id'],
        'url': x['url'],
        'topcolor': '#FF0000',
        'data': x['data'],
    }
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send'
    try:
        ret = appinstance.wxclient.post(url=url, data=data)
        '''
            ret: {
                "errcode": 0,
                "errmsg": "ok",
                "msgid": 200228332
            }
        '''
        return ret 
    except Exception, e:
        ret = {
            "errcode": 10000, 
            "errmsg": str(e),
        }
    return ret 

def send_weixin_text_notice(user, text):
    try:
        ret = appinstance.wxclient.send_text_message(user.openid, text)
        return ret 
    except Exception, e:
        ret = {
            "errcode": 10001, 
            "errmsg": str(e)  
        }
    return ret 

def autoNotice():
    break_flag = False 
    while True:
        if break_flag:
            break  
        unsent_notices = models.TipsLog.objects(status="unsent")
        if unsent_notices.count() <= 0:
            time.sleep(5) 
            print "Sleep 5s" 
        for i in unsent_notices:
            now = datetime.datetime.now() 
            add_time = i.add_time 

            '''是否延迟发放''' 
            delta = now - add_time 
            if delta.seconds < i.delay_time:
                continue 

            send_type = i.send_type 
            if send_type == 'weixin':
                if i.content_type == "dict":
                    weixin_data = json.loads(i.data) 
                    ret = send_weixin_notice(weixin_data)  
                elif i.content_type == "text":
                    ret = send_weixin_text_notice(i.user, i.data) 

                i.update(set__remark=ret['errmsg'])   
                if ret['errcode']: 
                    i.update(set__status="failure")
                else:
                    i.update(set__status="sent")
                    i.update(set__sent_time=now)  
                    try:
                        i.update(set__msg_id=ret['msgid']) 
                    except:
                        print traceback.print_exc() 

if __name__ == '__main__':
    with appinstance.app_context():
        autoNotice() 
