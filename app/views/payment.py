#coding:utf-8
'''
payment 模块，包括 移动web支付功能
'''
import random
import urllib
import time
import json
import traceback
import datetime

import bson
from flask import Blueprint, request, g, current_app, render_template, abort
from flask import redirect, url_for, make_response, session, jsonify

from app import models, libwxpay, cc, notice   

payment = Blueprint('payment',__name__) 

@payment.route('/pay_result')
def pay_result():
    # result=ok并不安全，应该用notify_url的结果
    # result = request.args['result']
    try:
        order_id = request.args['order_id']
        g.order = models.Order.objects.with_id(order_id)
        g.user = g.order.user 
        return redirect(url_for("ucenter.order"))  
    except:
        print traceback.print_exc()

@payment.route('/wxpay_notify', methods=['POST'])
def wxpay_notify():
    #to-do: 未实现成异步模式 
    now = datetime.datetime.now()
    notify = libwxpay.Notify_pub()
    notify.saveData(request.data)
    data = notify.getData()
    print 'payback notify', data
    if not notify.checkSign() or data['result_code'] != 'SUCCESS':
        notify.setReturnParameter('return_code', 'FAIL')
        print 'payback failed'
        return notify.returnXml()

    notify.setReturnParameter('return_code', 'SUCCESS')
    try:
        #订单支付成功 
        order = models.Order.objects.get(pay_id=data['out_trade_no']) 
        #订单已经处理或者正在处理    
        if order._wxCallbackDone():
            return notify.returnXml() 
        #交易单号&修改订单状态
        order.update(set__transaction_id=data['transaction_id'])
        '''修改订单状态'''
        order.setPaid()
        '''修改用户VIP天数'''
        buyer = order.user
        buyer.updateVip(order.product.days)
        '''相关收益分配'''
        cc.distributeCommissionForFriend(order)
        '''支付订单成功通知'''
        notice.buyOk(order.user, '', order)
    except:
        notify.setReturnParameter('return_code', 'FAIL')
        traceback.print_exc()

    return notify.returnXml()

@payment.route('/ajax_wxpay')
def ajax_wxpay():
    order = models.Order.objects.with_id(request.args['id'])
    try:
        if order.isPaid(): 
            return jsonify(dict(ret=1, msg=u'该订单已经支付.'))
        total_fee = order.fee 
        body = u'欢迎购买疯狂人脉说VIP服务'
        #unifiedorder
        uorder = libwxpay.UnifiedOrder_pub()
        uorder.setParameter('openid', str(order.user.openid))
        uorder.setParameter('body', body.encode("utf8"))  
        uorder.setParameter('out_trade_no', str(order.pay_id))
        uorder.setParameter('total_fee', str(int(float(total_fee)*100)))
        uorder.setParameter('notify_url', url_for('payment.wxpay_notify', _external=True))
        uorder.setParameter('trade_type', 'JSAPI')
        prepareId = uorder.getPrepayId()
        if not prepareId:
            msg = uorder.result.get('err_code_des') or uorder.result.get('return_msg') or u'未知错误'
            return jsonify(dict(ret=1, msg=msg))
        print 'prepareId', prepareId
        jsapi = libwxpay.JsApi_pub()
        jsapi.setPrepayId(prepareId)
        params = json.loads(jsapi.getParameters())
        print 'params', params
        return jsonify(dict(ret=0, params=params))
    except:
        print traceback.print_exc() 
