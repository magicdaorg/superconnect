#coding:utf-8
import time
import datetime 

import bson
from flask import Blueprint, request, g, current_app, render_template, abort
from flask import redirect, url_for, jsonify, make_response  
from app import models 
from mongoengine import Q 

m = Blueprint('m',__name__) 

@m.route('/')
def index():
    return 'm' 

@m.route('/list')
def list():
    follower_user = models.FansQueue.objects(user=g.user).first() 
    g.isUploaded = False 
    if follower_user:
        g.isUploaded = True 
    return render_template('m/list.html') 

@m.route('/group_list')
def group_list():
    g.isUploaded = True if models.FansQueue.objects(user=g.user).first() else False 
    return render_template('m/group_list.html') 

@m.route('/commission_rank')
def commission_rank():
    g.users = models.User.objects(commission__gt=0).order_by('-commission') 
    return render_template('m/commission_rank.html') 
    
@m.route('/ajax_download_user_data')
def ajax_download_user_data():
    try:
        start = int(request.args.get('start', 0))
        page_size= int(request.args.get('page_size', 20))  

        province = request.args.get('province', '') 
        city = request.args.get('city', '') 
        sex = request.args.get('sex', '') 

        list_type = request.args.get('list_type', 'personal') 
    except Exception, e:
        error = str(e)
        return jsonify({'ret': -1, 'error': error}) 

    filter = ''
    if province and province != u'省份':
        filter = Q(province=province) 
    if city and city != u'地级市':
        filter = filter & Q(city=city) 
    if sex and sex != u'不限':
        if filter:
            filter = filter & Q(sex=sex) 
        else:
            filter = Q(sex=sex) 

    if list_type == 'personal':
        pass 
    else:
        if filter:
            filter = filter & Q(qunimg_url__startswith='/upload') 
        else:
            filter = Q(qunimg_url__startswith='/upload')  

    if not filter:
        if list_type == 'personal':
            '''个人微信二维码''' 
            g.fans = models.FansQueue.objects[start: start+page_size] 
        else:
            g.fans = models.FansQueue.objects(qrimg_url__ne='')[start: start+page_size] 
    else:
        if list_type == 'personal':
            g.fans = models.FansQueue.objects(filter)[start: start+page_size] 
        else:
            g.fans = models.FansQueue.objects(filter)[start: start+page_size] 
    g.list_type = list_type 
    if g.fans:
        content = render_template('m/ajax_download_user_data.html') 
        res = {
            "ret": 0,
            "data": {
                "content": content  
            }
        }
        return jsonify(res) 
    else:
        error = u'内容已经加载完'
        return jsonify({"ret": -2, "error": error}) 

@m.route('/user_qr_ajax')
def user_qr_ajax():
    user_id = request.args.get('user_id')
    qr_type = request.args.get('qr_type', 'personal') 
    if not user_id:
        abort(404)

    try:
        g.follower_user = models.User.objects.with_id(user_id)
    except Exception, e:
        error = str(e)
        return error

    if not g.follower_user:
        abort(404)
    g.follower_user = models.FansQueue.objects(user=g.follower_user).first()

    g.qr_type = qr_type 
    return render_template('m/user_qr_ajax.html')

@m.route('/cmd', methods=['POST', ])
def cmd():
    try:
        cmd = request.form['cmd'] 
    except Exception, e:
        error = str(e)
        return jsonify({'ret': -1, 'error': error}) 
    if cmd not in ['top']:
        error = u'不支持%s命令!' % cmd 
        return jsonify({'ret': -2, 'error': error}) 

    follower_user = models.FansQueue.objects(user=g.user).first()
    if not follower_user:
        error = u'您还没有发布自己的二维码，请先点击右下方 更新二维码 发布自己的微信二维码!'
        return jsonify({'ret': -4, 'error': error}) 

    now = datetime.datetime.now() 
    last_refresh_time = follower_user.last_refresh_time 

    diff = last_refresh_time - now 
    if diff.days >= 0:
        error = u'自上次置顶刷新，还不足10分钟，请稍后重试!'
        return jsonify({'ret': -5, 'error': error})

    if not g.user.isVip():
        '''通过cookie方案来解决刷新置顶前需要添加的人数''' 
        '''这部分用户VIP过期，必须加3人才能刷新置顶''' 
        bad_buy = request.cookies.get('bad_buy', '') 
        if bad_buy:
            try:
                bad_buy = int(bad_buy) 
                if bad_buy > 0:
                    error = u'对不起!您的VIP会员已经到期，需要添加%s人才能置顶哟, 请先添加好友哟!' % bad_buy 
                    return jsonify({'ret': -10, 'error':error})  
            except:
                pass 

    now = datetime.datetime.now() + datetime.timedelta(minutes=10)    
    follower_user.update(set__last_refresh_time=now) 
    res = make_response(jsonify({'ret': 0, 'error': u'置顶成功'})) 
    return res 

