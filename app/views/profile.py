#coding:utf-8
import time
from datetime import datetime, timedelta  

import bson
from flask import Blueprint, request, g, current_app, render_template, abort
from flask import redirect, url_for, jsonify 
from app import models, uc 
from cStringIO import StringIO 
from werkzeug import secure_filename

profile = Blueprint('profile', __name__) 

@profile.route('/')
def index():
    return 'profile' 

@profile.route('/info/<id>')
def info(id):
    g.info = models.User.objects.with_id(id)
    g.fan = models.FansQueue.objects(user=g.info).first()  
    if not g.fan:
        return render_template('profile/error.html') 
    return render_template('profile/info.html') 

@profile.route('/group/<id>')
def group(id):
    g.info = models.User.objects.with_id(id)
    g.fan = models.FansQueue.objects(user=g.info).first()
    if not g.fan:
        return render_template('profile/error.html') 
    return render_template('profile/group.html') 
