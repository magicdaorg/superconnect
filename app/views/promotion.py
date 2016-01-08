#coding: utf8
import random
import urllib
import time
import datetime
import os 

import bson
from flask import Blueprint, request, g, current_app, render_template, abort
from flask import redirect, url_for, make_response, session

from app import models, qr 
import traceback 

promotion = Blueprint('promotion', __name__)

@promotion.route('/')
def index():
    return u'啊哈，访问其他页面试试' 

@promotion.route('/qrcode/<uid>')
def qrcode(uid):
    try:
        g.user = models.User.objects.with_id(uid) 
        if not g.user.isVip():
            g.error =  u'对不起！只有VIP会员，才拥有属于自己的专属二维码!' 
            return render_template('error.html') 
        g.qr_url = qr.getWwwQrImagePath(g.user)  
        return render_template('promotion/qrcode.html')
    except:
        traceback.print_exc() 

