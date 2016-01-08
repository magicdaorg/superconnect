#encoding: utf8
import qr
from flask import current_app
from mongoengine.errors import DoesNotExist, MultipleObjectsReturned
from app import models, app, uc
import time
import traceback
from app import uc
import random 
import datetime 

wxclient = app.wxclient

def sendMyMpQrImage(user, type=0):
    '''渠道Mp URL'''
    try:
        media = models.QrUser2MediaId.objects.get(user=user, type=type)
    except DoesNotExist:
        media = None
    except MultipleObjectsReturned:
        models.QrUser2MediaId.objects(user=user, type=type).delete()
        media = None
    now = int(time.time())
    if not media or (now - media.created_at) > 3*24*3600:
        '''推广二维码失效，微信服务器临时存储3天'''
        #先删除
        if media:
            media.delete()

        print u'上传二维码中...' % user
        localImgPath = qr.getLocalQrImagePath(user, type=type)

        try:
            ret = wxclient.upload_media("image", file(localImgPath))
        except:
            traceback.print_exc()
        print ret
        created_at = ret['created_at']
        media_id = ret['media_id']
        print media_id

        models.QrUser2MediaId(user=user, media_id=media_id, created_at=created_at, type=type).save()
    else:
        media_id = media.media_id

    ret = wxclient.send_image_message(user.openid, media_id)
    return ret


def _activityRedpack(motherid):
    try:
        user = models.User.objects.with_id(motherid) 
    except:
        return '' 


    def _getRandomNumber():
        data = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5] 
        weights = [0.75, 0.1, 0.05, 0.05, 0.01, 0.01, 0.01, 0.01, 0.01]  
        def weighted_choice_sub(weights):
            rnd = random.random() * sum(weights) 
            for i, w in enumerate(weights):
                rnd -= w
                if rnd < 0:
                    return i 
        index = weighted_choice_sub(weights) 
        return data[index] 

    now = datetime.datetime.now()  
    redpack = models.ExtractionCommissionLog.objects(user=user, activity_type="redpack", add_time__lt="%s 23:59:59" % now.strftime('%Y-%m-%d'), add_time__gt="%s 00:00:00" % now.strftime('%Y-%m-%d')).first()    
    if redpack:
        pass 
    else:
        redpack_number = _getRandomNumber() 
        models.ExtractionCommissionLog(user=user, activity_type="redpack", add_time=now, type=2, number=redpack_number, status=1).save()    

def handleScanCallback(message):
    if message.type != 'scan':
        return
    try:
        motherid = event_key = message.EventKey
        user_openid = message.source

        #推广人员带来新用户才下发红包，已经存在于系统中的用户扫描无效 
        if not models.User.objects(openid=user_openid).first():
            _activityRedpack(motherid) 

        uc.createUser(user_openid, motherid)
        print "User %s MotherId %s handleScanCallback" % (user_openid, motherid)
    except:
        traceback.print_exc()

def handleTemplateCallback(message):
    if message.type != 'templatesendjobfinish':
        return 
    msgId = message.MsgID
    status = message.Status 
    try:
        thisMsg = models.TipsLog.objects.get(msg_id=msgId)
    except DoesNotExist:
        print "MsgId %s 不存在!" % msgId 
        return 
    except MultipleObjectsReturned:
        return 

    thisMsg.update(set__remark=status) 

def sendRandomFansQrImage(user):
    totalCnt = models.FansQueue.objects().count() 
    index = random.randint(0, totalCnt) 
    fan = models.FansQueue.objects[index] 
    localImgPath = '%s%s' % ('/data/superconnect', fan.qrimg_url)  
    try:
        ret = wxclient.upload_media("image", file(localImgPath)) 
    except:
        traceback.print_exc() 
    media_id = ret['media_id'] 
    ret = wxclient.send_image_message(user.openid, media_id) 
    return ret 
