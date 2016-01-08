#coding: utf8
import datetime

from flask.ext.werobot import WeRoBot
from flask import current_app, g, url_for 
from werobot.reply import TransferCustomerServiceReply, ArticlesReply, Article 
from mongoengine.errors import DoesNotExist, MultipleObjectsReturned 

from app import models, uc, mp, redpack, notice  
import traceback 

robot = WeRoBot(enable_session=False)

@robot.text
def on_text(message):
    replay = '''
欢迎关注疯狂人脉说, 正在测试中, 如有疑问，请联系我们的客服: %s
想要加粉，赢取更多人脉，请进入我们的粉丝人脉，<a href="%s">点击开启超级人脉</a> 
您也可以发布自己的微信二维码，让人脉主动找到你，<a href="%s">点击进入</a>然后点击更新二维码 
             ''' % ('lizijie8', url_for('m.list', _external=True), url_for('m.list', _external=True))  
    return replay 

@robot.subscribe
def on_subscribe(message):
    try:
        event_key = message.EventKey  
        openid = message.source 
        if event_key and event_key.startswith('qrscene'):
            '''渠道统计Key''' 
            try:
                motherid = event_key.split('_')[1]  
                
                mother = models.User.objects.with_id(motherid) 
                #推广人员带来新用户才下发红包，已经存在于系统中的用户扫描无效 
                #if mother.isVip():
                #    if not models.User.objects(openid=openid).first():
                #        mp._activityRedpack(motherid) 
            except:
                motherid = uc.getVirtualUser()  

        else:
            motherid = uc.getVirtualUser() 
        g.user = uc.createUser(openid, motherid)  
        g.user.update(set__subscribe=1)
    except:
        print traceback.print_exc()
    reply = ArticlesReply(message=message) 
    article = Article(
        title=u'%s,10块钱轻松加爆5000粉丝，赚取1000倍以上推广佣金' % g.user.nickname,
        description=u'10块钱轻松加满5000微信好友！全部精准粉丝，主动加你好友！10块钱赚1000倍以上推广佣金！还在玩红包群',
        img='https://mmbiz.qlogo.cn/mmbiz/ItxyVrpob2m9xEnUCBtuJibQrPxFBn9zztWwHj93Ce1kpT3856N1HnrkCeMpo7gSXDV7STdQLJ39w7ydMLQnt5g/0?wx_fmt=jpeg',
        url='http://mp.weixin.qq.com/s?__biz=MzI3NzAyMzA4Ng==&mid=212273066&idx=1&sn=523ddfdcfac4f3753f09dcc2078bde91#rd' 
    )
    reply.add_article(article) 
    article = Article(
        title=u'【疯狂人脉说】功能全新启动！红包豪礼任性派！', 
        description=u'每天分享平台二维码，每日收红包,红包金额1元到100元随机发放.', 
        img='https://mmbiz.qlogo.cn/mmbiz/ItxyVrpob2nXhBFpu9UXkOlBEia9XS41pn7nElN1fx4gQrEuZakQ9uPajYXWHKkU1fAKiaRuQG5qRGnjbQSmDGjA/0?wx_fmt=jpeg', 
        url='http://mp.weixin.qq.com/s?__biz=MzI3NzAyMzA4Ng==&mid=400339876&idx=1&sn=64e27c1919dae605e6e28a147940209a#wechat_redirect' 
    )
    reply.add_article(article) 
    return reply  

@robot.unsubscribe
def on_unsubscribe(message):
    try:
        g.user = models.User.objects.get(openid=message.source)
        g.user.update(set__subscribe = 0) 
    except:
        pass
    return u'%s取消关注' % g.user

@robot.key_click('myqrcode')
def myqrcode(message):
    openid = message.source
    user = uc.createUser(openid, uc.getVirtualUser())
    if not user.isVip():
        reply = '''
对不起！只有VIP会员，才能生成永久性二维码！

<a href="%s">点击购买</a> 疯狂人脉说 VIP会员  
                ''' % 'http://v.fkduobao.com/sc/shop/buy?fr=menu'  
        return reply 
    else: 
        print u"发送%s推广二维码..." % user
        try:
            ret = mp.sendMyMpQrImage(user)
            print ret
        except:
            print traceback.print_exc()

@robot.key_click('random')
def random(message):
    openid = message.source 
    user = uc.createUser(openid, uc.getVirtualUser()) 
    try:
        ret = mp.sendRandomFansQrImage(user) 
        print ret 
    except:
        print traceback.print_exc() 

@robot.key_click('howtopublish')
def howtopublish(message):
    reply = '''
    您好！你可以点击右下角菜单，然后点击 进入粉丝人脉，再点击 右下角的 更新二维码，这样就可以上传您的微信二维码了，让别人主动加你，
生意主动找上门哟！
    或者 <a href="%s">点击这里</a>直达 粉丝人脉中心，更新二维码吧！  
''' % 'http://v.fkduobao.com/sc/m/list?fr=menu' 
    return reply 
    

@robot.handler
def template_callback(message):
    if message.type == 'templatesendjobfinish':
        '''处理模板消息回调函数'''
        mp.handleTemplateCallback(message)  
    elif message.type == 'scan':
        mp.handleScanCallback(message)
        reply = '''
感谢您关注疯狂人脉说
上传自己的个人二维码，吸引更多的人加你，有人脉，生意不难做! 

<a href="%s">点击进入</a>  疯狂人脉说 粉丝人脉中心  
                ''' % 'http://v.fkduobao.com/sc/m/list?fr=scan' 
        return reply
    else:
        pass

def init_app(app):
    robot.init_app(app)
