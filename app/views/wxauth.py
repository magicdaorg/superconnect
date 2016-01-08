#coding: utf8
from flask import g, render_template, request, redirect, url_for, make_response, session, Blueprint, current_app, Markup
from app import models 
import json
import datetime
import urllib
import urllib2 
import traceback  

wxauth = Blueprint('wxauth', __name__)

def formatBizQueryParaMap(paraMap, urlencode):
    """格式化参数，签名过程需要使用"""
    slist = sorted(paraMap)
    buff = []
    for k in slist:
        v = urllib.quote(paraMap[k]) if urlencode else paraMap[k]
        buff.append("{0}={1}".format(k, v))
    return "&".join(buff)

def createOauthUrlForCode(redirectUrl, scope="snsapi_base"):
    """生成可以获得code的url"""
    urlObj = {}
    urlObj["appid"] = current_app.config['WXAPP_ID']
    urlObj["redirect_uri"] = redirectUrl
    urlObj["response_type"] = "code"
    urlObj["scope"] = scope
    urlObj["state"] = "STATE"
    if scope == 'snsapi_userinfo':
        urlObj['state'] = 'qqg_getinfo'
    bizString = formatBizQueryParaMap(urlObj, True)
    return "https://open.weixin.qq.com/connect/oauth2/authorize?"+bizString+"#wechat_redirect"


@wxauth.route('/oauth')
def oauth():
    business_url = request.args.get('business_url', '')
    scope = request.args.get('scope', 'snsapi_base')
    redirect_uri = url_for('.oauth_result', business_url=business_url, _external=True)
    auth_url = createOauthUrlForCode(redirect_uri, scope)
    return redirect(auth_url)

@wxauth.route('/oauth_result')
def oauth_result():
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        business_url = request.args.get('business_url', '/')
        if not code:
            return  
        token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?' + urllib.urlencode({
            'appid': current_app.config['WXAPP_ID'],
            'secret': current_app.config['WXAPP_SECRET'],
            'code': code,
            'grant_type': 'authorization_code',
        })
        data = urllib.urlopen(token_url).read()
        j = json.loads(data)
        if 'openid' not in j:
            data = urllib.urlopen(token_url).read()
            j = json.loads(data)
        if 'openid' not in j:
            print j
            return u'获取信息失败，请返回重试。'
        session['openid'] = j['openid']
        #获取详情信息
        if state == 'qqg_getinfo':
                url = 'https://api.weixin.qq.com/sns/userinfo?' + urllib.urlencode({
                    'access_token': j['access_token'],
                    'openid': j['openid'],
                    'lang': 'zh_CN'
                })
                data = urllib.urlopen(url).read()
                try:
                    j = json.loads(data)
                except:
                    return redirect(business_url)
                if 'nickname' in j:
                    j['add_time'] = datetime.datetime.now()
                    j['vip_deadline'] = datetime.datetime.now()
                    j['update_info_time'] = datetime.datetime.now()
                    j['subscribe'] = 0
                    ret = models.User._get_collection().update({'openid': j['openid']}, {'$set': j}, upsert=True)
                    print 'updated userinfo', j['nickname']
                else:
                    print 'failed to get userinfo', j
        return redirect(business_url)
    except:
        print traceback.print_exc() 
