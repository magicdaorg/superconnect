#coding: utf8
import random
import urllib
import time
import datetime
import os
import bson
from flask import Blueprint, request, g, current_app, render_template, abort
from flask import redirect, url_for, make_response, session

test = Blueprint('test', __name__) 

@test.route('/')
def index():
    return render_template('test/index.html') 
