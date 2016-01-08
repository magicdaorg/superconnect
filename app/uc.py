#encoding: utf8 
from flask import current_app
from mongoengine.errors import DoesNotExist, MultipleObjectsReturned
import traceback 
import datetime 
from app import models

def getVirtualUser():
    return models.User.getVirtualUser() 

def createUser(openid, motherid):
    try:
        wxuser = current_app.wxclient.get_user_info(openid)
    except:
        traceback.print_exc()
        try:
            user = models.User.objects.get(openid=openid)
        except DoesNotExist:
            return None 
        return user  
    if wxuser.get('errcode'):
        print 'ERROR: get_user_info failed,', wxuser
        return None

    wxuser['update_info_time'] = datetime.datetime.now()
    wxuser['openid'] = openid
    ret = models.User.objects(openid=openid).update(__raw__={'$set': wxuser}, upsert=True, full_result=True)
    user = models.User.objects.get(openid=openid)
    if not user.promo_upline: #商城新用户
        #to-do: 第一次进入商城，通知上线
        virtualUser = getVirtualUser()  
        if not isinstance(motherid, models.User):
            motherid = models.User.objects.with_id( motherid )
            if not motherid:
                motherid = virtualUser 
        try:
            user.promo_upline = motherid 
        except:
            traceback.print_exc() 
        user.vip_deadline = datetime.datetime.now() 
        user.add_time = datetime.datetime.now() 
        user.save() 
        '''新用户加入新用户队列，方便其他队列对新用户进行处理''' 
        models.NewUserQueue(user=user).save() 
    user.save()
    return user

def updateUserinfo(openid):
    try:
        wxuser = current_app.wxclient.get_user_info(openid)
    except:
        traceback.print_exc()
        return None
    if wxuser.get('errcode'):
        print 'ERROR: get_user_info failed,', wxuser
        return None
    if not wxuser['subscribe']:
        return None
    wxuser['update_info_time'] = datetime.datetime.now()
    models.User.objects(openid=openid).update(__raw__={'$set': wxuser})
    print 'updated', wxuser['nickname']

def get3DownlineFriend(user, level=3):
    friends1 = []
    friends2 = []
    friends3 = []

    virtual_user = getVirtualUser()
    def _recursiveUserChain(user, friends1, friends2, friends3, depth=0):
        if depth >= 3 or depth >= level:
            return
        direct_downline_user = list(models.User.objects(promo_upline=user))
        if depth == 0:
            friends1 += direct_downline_user
        elif depth == 1:
            friends2 += direct_downline_user
        elif depth == 2:
            friends3 += direct_downline_user
        depth += 1
        for u in direct_downline_user:
            _recursiveUserChain(u, friends1, friends2, friends3, depth)
    _recursiveUserChain(user, friends1, friends2, friends3)
    return friends1, friends2, friends3
