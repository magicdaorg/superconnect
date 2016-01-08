#coding: utf8 
from flask import Flask, session, g, url_for, request, redirect    
from flask.ext.mongoengine import MongoEngine
import werobot.client 
import datetime 
import urllib2  

app = Flask(__name__)
app.config.from_object("config.SuperConnect")  

db = MongoEngine()
db.init_app(app)  

# 微信基础服务公用token
@property
def get_common_token(self):
    now = datetime.datetime.now()
    try:
        item = models.Config.objects.get(name='wx:access_token')
        g.wx_token = item['value']
    except:
        g.wx_token = None
    if not g.wx_token or g.wx_token['deadline'] <= now:
        g.wx_token = self.grant_token()
        if g.wx_token.get('errcode'):
            print 'get_common_token: ', g.wx_token
            return None
        g.wx_token['deadline'] = now + datetime.timedelta(seconds=g.wx_token['expires_in'])
        models.Config.objects(name='wx:access_token').update(set__value=g.wx_token, upsert=True)
    return g.wx_token['access_token']

werobot.client.Client.token = get_common_token

# 微信基础服务接口对象
app.wxclient = werobot.client.Client(app.config['WXAPP_ID'], app.config['WXAPP_SECRET'])

from app import views, models
import uc
import libwxpay
import cc
import notice
import mp
import redpack 

@app.before_request
def before_request(): 
    if request.path.startswith('/admin') or request.path.startswith('/sc/robot') or  request.path.startswith('/sc/wxauth') or request.path.startswith('/sc/wechatjs') or \
        request.path.startswith('/sc/payment') or request.path.startswith('/static') or request.path.startswith('/sc/m/user_qr_ajax') or \
        request.path.startswith('/sc/m/ajax_download_user_data') or request.path.startswith('/sc/articles'):
        return 

    g.debug = request.args.get('debug', 'false').strip().lower()  
    if g.debug == 'true':
        openid = request.args.get('openid', 'obmdTw4eo6ACVP5W8zvYyyhpuODA') 

    #如果没有openid则跳到授权页面
    if g.debug == 'true':
        openid = session.get('openid', openid)
    else:
        openid = session.get('openid') 

    g.config = app.config  
    if not openid:
        url = url_for('wxauth.oauth', business_url=request.url) 
        return redirect(url)

    #创建用户 或者 返回该用户信息  
    query = urllib2.urlparse.urlparse(request.url).query
    try:
        query = dict( [ i.split("=") for i in query.split("&") ] ) 
    except:
        query = dict() 
    motherId = query.get("motherid", uc.getVirtualUser())  
    g.user = uc.createUser(openid, motherId) 

    if not (g.user and g.user.nickname):
        url = url_for('wxauth.oauth', business_url=request.url, scope='snsapi_userinfo')
        return redirect(url) 

    # 授权成功，获取用户信息
    try:
        g.user = models.User.objects.get(openid=openid)
        now = datetime.datetime.now()
        if not g.user.update_info_time or g.user.update_info_time + datetime.timedelta(days=1) < now:
            uc.updateUserinfo(openid)
    except DoesNotExist:
        pass 
