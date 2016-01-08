#coding: utf8 
from flask.ext import admin  
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask.ext.admin import expose, BaseView
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple
from app import app, models  


class MyIndexView(admin.AdminIndexView):
    @expose('/', methods=['GET','POST'])
    def index(self):
        return redirect('/admin/user') 

panel = admin.Admin(app, u'疯狂人脉说', index_view=MyIndexView(), template_mode="bootstrap3")  
from views import *  

panel.add_view(UserView(models.User, name=u'用户管理', category=u'主页')) 
panel.add_view(ProductView(models.Product, name=u'套餐管理', category=u'主页')) 

panel.add_view(OrderView(models.Order, name=u'订单列表')) 

panel.add_view(ArticleViewNew(models.Article, name=u'创建文章', category=u'素材编辑'))  

panel.add_view(CommissionLogView(models.CommissionLog, name=u'佣金日志', category=u'日志'))
panel.add_view(ExtractionCommissionLogView(models.ExtractionCommissionLog, name=u'提取', category=u'日志'))
panel.add_view(TipsLogView(models.TipsLog, name=u'微信提醒日志', category=u'日志'))

panel.add_view(FansQueueView(models.FansQueue, name=u'粉丝人脉')) 

if __name__ == '__main__':
    app.debug = True
    _app = DispatcherMiddleware(
        app, {
        })
    run_simple('0.0.0.0', 2990, _app, use_reloader=False, use_debugger=True, threaded=True)
