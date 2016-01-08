#coding: utf8
import random
import urllib
import time
import datetime
import os
import bson
from flask import Blueprint, request, g, current_app, render_template, abort
from flask import redirect, url_for, make_response, session

from app import models 
import traceback

articles = Blueprint('articles', __name__)

@articles.route('/i/<_id>')
def i(_id):
    g.article = models.Article.objects.with_id(_id) 
    return render_template('article/view.html') 
