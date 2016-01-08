#coding:utf-8
import time
from datetime import datetime, timedelta  

import bson
from flask import Blueprint, request, g, current_app, render_template, abort, make_response 
from flask import redirect, url_for, jsonify 
from app import models, uc 
from cStringIO import StringIO 
from werkzeug import secure_filename
from app.helper import allowed_file, create_thumbnai, handle_head_image, handle_qr_image, handle_qun_image

ucenter = Blueprint('ucenter',__name__) 

@ucenter.route('/')
def index():
    return render_template('ucenter/index.html') 


@ucenter.route('/order')
def order():
    g.orders = models.Order.objects(user=g.user) 
    return render_template('ucenter/order.html') 

@ucenter.route('/wallet', methods=['POST', 'GET'])
def wallet():
    '''佣金提现函数''' 
    if request.method == 'GET':
        g.m_list = models.ExtractionCommissionLog.objects(user=g.user) 
        return render_template('ucenter/wallet.html')  
    else:
        try:
            fee = float(request.form['fee']) 
        except Exception, e:
            error = str(e)
            return jsonify({'ret': -1, "error": error} ) 

        if fee <= 0:
            error = u'亲，提取金额必须大于0哟!'
            return jsonify({"ret": -2, "error": error}) 

        if fee > g.user.getWithCommissionSafe():
            error = u'亲，余额积分不足!'
            return jsonify({"ret": -3, "error": error})

        models.ExtractionCommissionLog(user=g.user, number=fee).save() 
        '''减去未提现积分''' 
        g.user.update(dec__with_commission=fee) 
        return jsonify({"ret": 0}) 

@ucenter.route('/list/<int:level>')
def list(level):
    if level not in [1, 2, 3]:
        abort(404) 
    g.level = level  
    return render_template('ucenter/list.html') 

@ucenter.route('/list_ajax')
def list_ajax():
    level = int(request.args.get('level', 1))
    if level not in [1, 2, 3]:
        return jsonify({'ret': -1, 'error': u'level not in [1, 2, 3]'}) 
    g.friends = uc.get3DownlineFriend(g.user, level)[level-1]  
    content = render_template('ucenter/list_ajax.html') 
    res = {
        "ret": 0,
        "data": {
            "content": content 
        }
    }
    return jsonify(res) 

@ucenter.route('/upload_ajax', methods=['POST', ])
def upload_ajax():
    try:
        image_type = request.form['image_type']
        image_file = request.files['image']
    except Exception, e:
        error = str(e)
        return jsonify({"ret": -1, "error": error})
    if image_type not in ['head', 'qr', 'qun']:
        return jsonify({'ret': -2, "error": u'上传的图片类型不符合规范.'})

    image_content = StringIO( image_file.read()) 

    if not allowed_file(image_content):
        return jsonify({'ret': -3, "error": u'只允许上传图片文件.'})

    if image_type == 'head':
        ret = handle_head_image(g.user, image_content)
    elif image_type == 'qr':
        ret = handle_qr_image(g.user, image_content)
    elif image_type == 'qun':
        ret = handle_qun_image(g.user, image_content) 
    return jsonify(ret)

@ucenter.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'GET':
        if not g.user.isVip():
            upload_bad_buy = request.cookies.get("upload_bad_buy", "") 
            if not upload_bad_buy:
                g.error =  u'对不起！只有VIP会员，才能发布自己的二维码到疯狂人脉说 粉丝人脉 中!, 或者进入【粉丝人脉】中心加满15人用户，亦可免费发布或者更新二维码！' 
                res = make_response( render_template('error.html')  ) 
                res.set_cookie("upload_bad_buy", "15", max_age=365*24*60*60)  
                return res 
            elif int(upload_bad_buy) > 0:
                g.error =  u'对不起！只有VIP会员，才能发布自己的二维码到疯狂人脉说 粉丝人脉 中!, 您还需要添加%s人才能发布或者更新个人二维码，继续加油！！！' % upload_bad_buy  
                return render_template("error.html") 
            else:
                pass 

        g.fan = models.FansQueue.objects(user=g.user).first() 
        res = make_response( render_template('ucenter/upload.html') )
        if g.user.isVip():
            return res 
        else:
            res.set_cookie("upload_bad_buy", "15", max_age=365*24*60*60)
            return res 
    else:
        try:
            nickname = request.form['nickname']
            wechat = request.form['wechat']
            desc = request.form['desc']
            qun_desc = request.form['qun_desc'] 

            photo_url = request.form['photo_url']
            qrimg_url = request.form['qrimg_url']
            qunimg_url = request.form['qunimg_url'] 

            province = request.form['province'] 
            city = request.form['city'] 

            sex = request.form['sex'] 
        except:
            error = u'相关参数不完整，请认真填写!'
            return jsonify({'ret': -1, "error": error})
        #last_refresh_time = datetime.now() + timedelta(minutes=10)
        models.FansQueue.objects(user=g.user).update(set__photo_url=photo_url, set__qrimg_url=qrimg_url, set__nickname=nickname, 
            set__wechat=wechat, set__desc=desc, set__province=province, set__city=city, set__sex=sex, set__qunimg_url=qunimg_url,
            set__qun_desc=qun_desc, upsert=True)

        res = {
            "ret": 0,
            "data": {
                "url": url_for('m.list')
            }
        }
        return jsonify(res)

@ucenter.route('/money')
def money():
    g.orders = models.CommissionLog.objects(user=g.user) 
    return render_template('ucenter/money.html') 
