#coding:utf-8
import time
import datetime 

import bson
from flask import Blueprint, request, g, current_app, render_template, abort
from flask import redirect, url_for, jsonify 
from app import models 

shop = Blueprint('shop',__name__) 

@shop.route('/')
def index():
    return 'shop' 

@shop.route('/buy', methods=['GET', 'POST']) 
def buy():
    if request.method == 'GET':
        g.products = models.Product.objects(display=True) 
        return render_template('shop/buy.html') 
    else:
        try:
            pid = request.form['pid'] 
            username = request.form['username'] 
            tel = request.form['tel'] 
        except:
            error = u'相关参数不完整, 请认真填写!' 
            return jsonify({'ret': -1, "error": error}) 

        try:
            product = models.Product.objects.with_id(pid)
        except Exception, e:
            error = str(e)
            return jsonify({'ret': -2, 'error': error})

        '''保存相关信息'''
        g.user.update(set__realname=username) 
        g.user.update(set__telephone=tel) 

        '''创建Order''' 
        pay_id = 'H%s%s' % (datetime.datetime.now().strftime('%Y%m%d'), int(time.time())) 
        fee = product.fee 
        order = models.Order(user=g.user, product=product, fee=fee, pay_id=pay_id, status=0)
        order.save() 

        res = {
            "ret": 0,
            "data": {
                "redirect_url": url_for('shop.order', order_id=str(order.id))    
            }
        }
        return jsonify(res) 

@shop.route('/order/<order_id>')
def order(order_id):
    try:
        g.order = models.Order.objects.with_id(order_id) 
        if not g.order:
            abort(404)  
    except:
        abort(404) 
    return render_template('shop/order.html') 
