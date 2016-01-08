#coding: utf8
from flask import g, render_template, request, redirect, url_for, make_response, session, Blueprint, current_app
import traceback 
import random 
import string 
import urllib 
import time 
import json 
import hashlib 

wechatjs = Blueprint('wechatjs', __name__)

class JsSDKSign:
    def __init__(self):
        self.js_ticket = ''
        self.js_ticket_expires_at = 0

    def __get_jsticket(self):
        now = int(time.time())
        if self.js_ticket_expires_at - now > 60:
            return self.js_ticket
        url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi' % self.token
        data = urllib.urlopen(url).read()
        j = json.loads(data)
        if j['errcode'] != 0:
            print 'error', j
            return ''
        self.js_ticket = j['ticket']
        self.js_ticket_expires_at = j['expires_in'] + now
        return self.js_ticket


    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self, url, token):
        self.token = token
        self.url = url
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': self.__get_jsticket(),
            'timestamp': self.__create_timestamp(),
            'url': self.url
        }
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret

sign = JsSDKSign()

@wechatjs.route('/config')
def account():
    try:
        g.sign = sign.sign(request.headers.get('Referer', request.url), current_app.wxclient.token)
        debug = request.args.get('debug', 'false')
        js = '''
        wx.config({
            debug: %s, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
            appId: '%s', // 必填，公众号的唯一标识
            timestamp: %s, // 必填，生成签名的时间戳
            nonceStr: '%s', // 必填，生成签名的随机串
            signature: '%s',// 必填，签名，见附录1
            jsApiList: ['onMenuShareTimeline', 'onMenuShareAppMessage', 'hideOptionMenu', 'showOptionMenu'] // 必填，需要使用的JS接口列表，所有JS接口列表见附录2
        });
        ''' % (debug, current_app.config['WXAPP_ID'], g.sign['timestamp'], g.sign['nonceStr'], g.sign['signature'])
        resp = make_response(js)
        resp.headers['Control-Cache'] = 'no-cache'
        resp.headers['Content-Type'] = 'text/javascript; charset=utf-8'
        return resp
    except:
        print traceback.print_exc() 
