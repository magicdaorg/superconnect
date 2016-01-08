#encoding: utf8
from flask import Flask, request, url_for, session, Markup, render_template, g, abort, make_response, redirect, flash, Markup, jsonify,Response
from flask.ext.admin.actions import action
from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.admin.contrib.mongoengine.filters import * 
from flask.ext.admin.model.template import macro
from flask.ext.admin import form, expose, BaseView 
import os 
from flask_admin.form import rules 
from app import app, models, uc  
from app.helper import allowed_file, create_thumbnai, handle_head_image, handle_qr_image 
import time 

@app.before_request
def before_request():
    if not request.path.startswith('/admin'):
        return abort(403)
    auth = request.authorization
    if (auth and (auth.username == 'admin' and auth.password == 'admin123')):
        return
    else:
        return Response( u'请登陆', 401, {'WWW-Authenticate': 'Basic realm="login"'})

class UserView(ModelView):
    column_labels = {
        "nickname": u'昵称',
        "subscribe": u'是否关注', 
        "sex": u'性别', 
        "country": u'位置', 
        "add_time": u'关注时间',
        "promo_upline": u'我的上级',
        "friends_cnt": u'我的人脉',
        "commission": u'累计收入',
        "with_commission": u'可提现收入',
        "channel_id": u'渠道ID',
        "vip_deadline": u'VIP过期时间',
        "telephone": u'手机号',
        "realname": u'预留姓名',
        "wechat": u'微信号' 
    }

    form_ajax_refs = {
        "promo_upline": {
            "fields": ['nickname'],
            "page_size": 20 
        }
    }
    #can_delete = False 
    column_filters = [
        FilterEqual(models.User.sex, u'性别', options=((1, u'男'), (0, u'女'))), 
        FilterEqual(models.User.subscribe, u'是否关注', options=((1, u'是'), (0, u'否'))), 
        FilterEqual(models.User.channel_id, u'用户渠道'),
        DateTimeGreaterFilter(models.User.vip_deadline, u'VIP会员'),  
        DateTimeBetweenFilter(models.User.add_time, u'用户关注时间')  
    ] 

    def _nickname(v,c,m,p):
        if m.nickname:
            return Markup('<img src="%s" width="32" />%s' % (m.headimgurl[:-2] + '/46', m.nickname))
        return Markup(u'这个用户很懒，什么都没留下!')
    column_formatters = {
        "nickname": _nickname,
        "country": lambda v,c,m,p: '%s/%s/%s' % (m.city, m.province, m.country),
        "friends_cnt": lambda v,c,m,p: '%s/%s/%s/%s' % (m.friends_cnt, m.friends1_cnt, m.friends2_cnt, m.friends3_cnt),
        "subscribe": lambda v,c,m,p: u'是' if m.subscribe == 1 else u'否',
        "sex": lambda v,c,m,p: u'男' if m.sex == 1 else u'女',
        "commission": lambda v,c,m,p: Markup('<a href="./c/%s">%s</a>' % (m.id, m.commission))  
    }
    column_exclude_list = ('headimgurl', 'subscribe_time', 'update_info_time', 'province', 'city', 'friends1_cnt', 'friends2_cnt', 'friends3_cnt') 
    column_searchable_list = ('nickname', 'openid', 'telephone', 'channel_id') 

    @expose('/c/<_id>')
    def c(self, _id):
        user = models.User.objects.with_id(_id) 
        commissions = models.CommissionLog.objects(user=user) 
        return self.render('admin/user/commission.html', commissions=commissions, user=user) 



class ProductView(ModelView):
    column_labels = {
        "name": u'产品名字',
        "fee": u'单价(元)', 
        "month": u'时长，单位月',
        "days": u'时长，单位日',  
        "default_checked": u'默认产品，只能勾选一个',
        "remark": u'特惠消息', 
        "display": u'是否上线' 
    }

    can_delete = False 

class OrderView(ModelView):
    column_labels = {
        'user': u'订单人', 
        "product": u'套餐类型', 
        "add_time": u'下单时间', 
        "fee": u'总金额', 
        "pay_id": u'订单号', 
        "transaction_id": u'微信交易号',
        "status": u'订单状态' 
    }
    column_formatters = {
        "status": lambda v,c,m,p: m.getStatusName() ,  
        "user": lambda v,c,m,p: '%s[%s]' % (m.user.nickname, m.user.add_time.strftime('%Y-%m-%d'))   
    }

    column_filters = [
        FilterEqual(models.Order.status, u'是否支付', options=[(0, u'待付款'), (1, u'已支付')]),  
        DateTimeBetweenFilter(models.Order.add_time, u'购买时间'), 
    ]

    column_searchable_list = ('pay_id', ) 

    can_delete = False 
    form_ajax_refs = {
        "user": {
            "fields": ['nickname'],
            "page_size": 20 
        }
    }

class CommissionLogView(ModelView):
    column_labels = {
        "user": u'收益人', 
        "order": u'提成订单',
        "add_time": u'收益时间',
        "commission": u'提成收益' 
    } 
    can_delete = False 
    form_ajax_refs = {
        "user": {
            "fields": ['nickname'],
            "page_size": 20 
        }
    }

class ExtractionCommissionLogView(ModelView):
    can_create = False  
    can_delete = False 
    can_edit = True
    column_labels = {
        "user":  u'提取人', 
        "add_time": u'提取时间', 
        "number": u'提取金额', 
        "status": u'提取状态',
        "sent_time": u'发放时间', 
        "remark": u'备注信息' 
    }
    column_formatters = {
        'type': lambda v,c,m,p: m.getType(),  
        "status": lambda v,c,m,p: m.getStatusName(),
        'number': lambda v,c,m,p: Markup('<a href="./log/%s">%s</a>' % (m.id, m.number))   
    }
    form_ajax_refs = {
        "user": {
            "fields": ['nickname'],
            "page_size": 20 
        }
    }

    @action('sent', u'通过申请', u'确认通过用户提取金额(一旦确认，立即发放红包)?')
    def sent(self, ids):
        for i in ids:
            ref = models.ExtractionCommissionLog.objects.with_id(i) 
            if ref.status in [2, 4]:
                #状态：待发放, 打款失败  
                ref.update(set__status=1) 

    @expose('/log/<mid>')
    def log(self, mid):
        commission_ref = models.ExtractionCommissionLog.objects.with_id(mid) 
        logs = models.RedpackLog.objects(commission_ref=commission_ref) 
        return self.render('admin/admin_redpack_logs.html', logs=logs)     

class FansQueueView(ModelView):
    column_labels = {
        "user": u'用户',
        "photo_url": u'头像',
        "qrimg_url": u'个人微信二维码',
        "qunimg_url": u'微信群二维码', 
        "nickname": u'昵称',
        "wechat": u'微信号',
        "desc": u'个人描述',
        "qun_desc": u'群描述', 
        "province": u'省份',
        "city": u'城市',
        "sex": u'性别', 
        "last_refresh_time": u'置顶时间' 
    }
    column_formatters = {
        "photo_url": lambda v,c,m,p: Markup('<img src="%s" width=64 height=64 />' % m.photo_url),
        "qrimg_url": lambda v,c,m,p: Markup('<img src="%s" width=64 height=64 />' % m.qrimg_url),  
        "qunimg_url": lambda v,c,m,p: Markup('<img src="%s" width=64 height=64 />' % m.qunimg_url if m.qunimg_url else u'未上传'),  
    }

    form_ajax_refs = {
        "user": {
            "fields": ['nickname'],
            "page_size": 20 
        }
    }

    column_searchable_list = ('nickname', 'province', 'city', 'sex', 'wechat') 

    form_extra_fields = {
        "photo_url": form.ImageUploadField(u'头像', base_path="/data/superconnect/upload/tmp", thumbnail_size=(80, 80, True), namegen=lambda o,f: '%s.jpeg' % int(time.time())),  
        "qrimg_url": form.ImageUploadField(u'微信二维码', base_path="/data/superconnect/upload/tmp", thumbnail_size=(80, 80, True), namegen=lambda o,f: '%s.jpeg' % int(time.time() + 10))  
    } 

    def on_model_change(self, form, model, is_created):
        photo_url = model.photo_url 
        qrimg_url = model.qrimg_url 
        upload_dir = "/data/superconnect/upload/tmp/%s"  
        local_photo_url = upload_dir % photo_url 
        local_qrimg_url = upload_dir % qrimg_url 

        dst_qrimg_url = "%s/%s_q.jpeg" % (app.config['UPLOAD_FANS_DIR'], model.user.id)  
        '''修改QR路径''' 
        os.system("cp -rf %s %s" % (local_qrimg_url, dst_qrimg_url)) 
        '''修改头像路径''' 
        dst_origin_photo_url = "%s/%s_o.jpeg" % (app.config['UPLOAD_FANS_DIR'], model.user.id) 
        os.system("cp -rf %s %s" % (local_photo_url, dst_origin_photo_url)) 
        '''头像缩略图''' 
        thumbnail_img = "%s_thumb.jpg" % photo_url.split(".")[0] 
        local_thumbnail_url = upload_dir % thumbnail_img  
        dst_thumbnail_photo_url = "%s/%s_t.jpeg" % (app.config['THUMBNAIL_FOLDER'], model.user.id) 
        os.system("cp -rf %s %s" % (local_thumbnail_url, dst_thumbnail_photo_url)) 

        '''修改存在数据库中的url'''
        model.photo_url = "%s/%s_t.jpeg" % ("/upload/thumbnail", model.user.id)  
        model.qrimg_url = "%s/%s_q.jpeg" % ("/upload/fans", model.user.id) 
        '''修改权限''' 
        os.system("chown nginx.nginx %s" % dst_origin_photo_url) 
        os.system("chown nginx.nginx %s" % dst_thumbnail_photo_url) 
        os.system("chown nginx.nginx %s" % dst_qrimg_url) 
        

class TipsLogView(ModelView):
    pass 

class ArticleViewNew(ModelView):
    create_template = 'admin/page_article_edit.html'
    edit_template = 'admin/page_article_edit.html' 

    column_labels = {
        "title": u'文章标题',
        "author": u'文章作者',
        "content": u'文章内容',
        "new": u'是否有New标志',
        "hot": u'是否有Hot标志',
        "add_time": u'创建时间',
        "display": u'是否显示' 
    }
    column_formatters = {
        "title": lambda v,c,m,p: Markup('<a href="%s/sc/articles/i/%s?debug=true" target="_blank">%s</a>' % (app.config['DOMAIN'], m.id, m.title)), 
    }

    form_widget_args = {
        "content": {
            "class": "form-control ckeditor"
        }
    }
