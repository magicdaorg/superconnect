#coding: utf8 
from app import app 
import test 
import robot 
import wxauth 
import ucenter 
import shop 
import m 
import wechatjs 
import payment 
import promotion 
import articles
import profile 

#注册Blueprint 
app.register_blueprint(test.test, url_prefix='/sc/test')  
app.register_blueprint(wxauth.wxauth, url_prefix='/sc/wxauth')  
app.register_blueprint(ucenter.ucenter, url_prefix='/sc/ucenter')  
app.register_blueprint(shop.shop, url_prefix='/sc/shop')  
app.register_blueprint(m.m, url_prefix='/sc/m')  
app.register_blueprint(wechatjs.wechatjs, url_prefix='/sc/wechatjs') 
app.register_blueprint(payment.payment, url_prefix=u'/sc/payment') 
app.register_blueprint(promotion.promotion, url_prefix=u'/sc/promotion') 
app.register_blueprint(articles.articles, url_prefix=u'/sc/articles') 
app.register_blueprint(profile.profile, url_prefix=u'/sc/profile') 

robot.init_app(app)
