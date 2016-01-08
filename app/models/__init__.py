#coding: utf8 
import datetime 
from app import db 
from mongoengine.errors import DoesNotExist, MultipleObjectsReturned  
from flask.ext.mongoengine import mongoengine 
import time 

class User(db.Document):
    '''用户管理''' 
    nickname = db.StringField(max_length=100, verbose_name=u'昵称', default='')
    headimgurl = db.StringField(max_length=500, default='', verbose_name=u'头像链接')
    subscribe = db.IntField(verbose_name=u'是否关注公众号', default=0)
    subscribe_time = db.IntField(verbose_name=u'关注时间')
    sex = db.IntField(verbose_name=u'性别')
    country = db.StringField(max_length=30, verbose_name=u'国家', default='')
    province = db.StringField(max_length=30, verbose_name=u'省份', default='')
    city  = db.StringField(max_length=30, verbose_name=u'城市', default='')
    openid = db.StringField(max_length=50, unique=True, verbose_name=u'OpenID')
    unionid = db.StringField(max_length=50, verbose_name=u'UnionId') 
    add_time = db.DateTimeField(default=datetime.datetime.now, verbose_name=u'创建时间')
    update_info_time = db.DateTimeField(default=datetime.datetime.now, verbose_name=u'资料更新时间')

    telephone = db.StringField(default='', max_length=20)
    realname = db.StringField(max_length=100, verbose_name=u'真实姓名', default='') 
    wechat = db.StringField(max_length=30) 

    promo_upline = db.ReferenceField('User',verbose_name=u'我的上级') 

    friends_cnt = db.IntField(default=0, verbose_name=u'总用户数') 
    friends1_cnt = db.IntField(default=0, verbose_name=u'一级用户') 
    friends2_cnt = db.IntField(default=0, verbose_name=u'二级用户')
    friends3_cnt = db.IntField(default=0, verbose_name=u'三级用户') 

    commission = db.FloatField(default=0.0, verbose_name=u'累计佣金')
    with_commission = db.FloatField(default=0.0, verbose_name=u'可提现佣金') 

    channel_id = db.StringField(default='', max_length=20, verbose_name=u'用户渠道ID')  

    vip_deadline = db.DateTimeField(default=datetime.datetime.now, verbose_name=u'VIP截至日期')  
    meta = {
        "ordering": ["-id"] 
    }

    def __unicode__(self):
        if not self.nickname:
            return ''  
        if len(self.nickname) > 10:
            return self.nickname[:10]
        return self.nickname 

    def isVip(self):
        now = datetime.datetime.now() 
        diff = self.vip_deadline - now 
        return diff.days >= 0   

    def getCommission(self):
        return self.commission

    def getWithCommission(self):
        return self.with_commission
    
    def getMyPromo(self):
        return self.promo_upline 

    def getMyPromoName(self):
        if self.promo_upline.isVirtualUser():
            return u'疯狂人脉说'
        else:
            return self.promo_upline 

    def getFriendsCnt(self):
        return self.friends_cnt

    def getFriends1Cnt(self):
        return self.friends1_cnt

    def getFriends2Cnt(self):
        return self.friends2_cnt

    def getFriends3Cnt(self):
        return self.friends3_cnt

    def getWithCommissionSafe(self):
        return self.with_commission 

    def updateVip(self, days):
        if self.isVip():
            start_time = self.vip_deadline 
        else:
            start_time = datetime.datetime.now() 
        new_deadline = start_time + datetime.timedelta(days=days) 
        self.update(set__vip_deadline=new_deadline) 

    def isVirtualUser(self):
        return self.openid == 24*'0'

    @staticmethod
    def getVirtualUser():
        _id = 24 * '0' 
        openid = _id 
        user, created = User.objects.get_or_create(id=_id, defaults={'openid': openid}) 
        user.update(set__nickname=u'虚拟上线') 
        return user 

    @mongoengine.queryset_manager
    def vips(doc_cls, queryset):
        now = datetime.datetime.now() 
        return queryset.filter(vip_deadline__gt=now)  

class Config(db.Document):  
    name = db.StringField(max_length=30, primary_key=True, verbose_name=u'变量名')
    value = db.DynamicField(verbose_name=u'值')

class Product(db.Document):
    name = db.StringField(max_length=200, verbose_name=u'产品名字') 
    fee = db.FloatField(default=0.0, verbose_name=u'单价') 
    month = db.IntField(default=1, verbose_name=u'时长，单位月') 
    days = db.IntField(default=30, verbose_name=u'时长，单位天') 


    default_checked = db.BooleanField(default=False, verbose_name=u'默认产品，只能勾选一个') 
    remark = db.StringField(max_length=100, verbose_name=u'特惠信息')  
    display = db.BooleanField(default=False, verbose_name=u'是否上线') 

    def __unicode__(self):
        return self.name 

    meta = {
        "ordering": ['days'] 
    }

class Order(db.Document):
    user = db.ReferenceField('User', reverse_delete_rule=db.CASCADE, verbose_name=u'购买者') 
    product = db.ReferenceField('Product', reverse_delete_rule=db.CASCADE, verbose_name=u'套餐') 
    add_time = db.DateTimeField(default=datetime.datetime.now, verbose_name=u'订单时间') 

    fee = db.FloatField(default=0.0, verbose_name=u'金额') 
    pay_id = db.StringField(max_length=50, unique=True, verbose_name=u'订单编号') 
    transaction_id = db.StringField(default='', verbose_name=u'支付单号') 

    status = db.IntField(default=0, choices=[(0, u'待付款'), (1, u'已支付')], verbose_name=u'订单状态') 

    meta = {
        "ordering": ['-id'] 
    }

    def __unicode__(self):
        return u'%s(%s)' % (self.user, self.product) 

    def isPaid(self):
        return self.status == 1 

    def setPaid(self):
        self.update(set__status=1) 

    def _wxCallbackDone(self):
        return self.transaction_id != ''  

    def getStatusName(self):
        status_map = dict([('0', u'待付款'), ('1', u'已支付')])  
        return status_map[str(self.status)] 

class CommissionLog(db.Document):
    user = db.ReferenceField('User', reverse_delete_rule=db.CASCADE, verbose_name=u'受益人')
    order = db.ReferenceField('Order', reverse_delete_rule=db.CASCADE, verbose_name=u'提成订单来源') 
    add_time = db.DateTimeField(default=datetime.datetime.now, verbose_name=u'分配时间')  
    commission = db.FloatField(default=0.0, verbose_name=u'提成金额')  
    meta = {
        "ordering": ["-id"] 
    }

class ExtractionCommissionLog(db.Document):
    '''提取收益详情'''  
    type = db.IntField(default=1, verbose_name=u'打款方式', choices=[(1, u'微信企业打款'), (2, u'微信红包'), (3, u'支付宝')])   
    user = db.ReferenceField('User', reverse_delete_rule=db.CASCADE, verbose_name=u'提取用户')
    add_time = db.DateTimeField(default=datetime.datetime.now, verbose_name=u'申请时间') 

    number = db.FloatField(default=0.0, verbose_name=u'提取金额') 
    status = db.IntField(default=2, choices=[(1,  u'通过申请'), (2, u'待发放'), (3, u'驳回申请'), (4, u'打款异常,请稍等'), (5, u'已发放')])
    sent_time = db.DateTimeField(verbose_name=u'佣金发放时间')
    remark = db.StringField(verbose_name=u'备注信息') 

    mch_billno = db.StringField(verbose_name=u'微信交易单号', default='') 
    activity_type = db.StringField(default="generous", choices=[('generous', u'普通类型'), ('redpack', u'红包活动')]) 

    def isSent(self):
        return self.status ==  5   

    def isMch(self):
        return self.type == 1

    def isWechatRedpack(self):
        return self.type == 2

    def isZhifubao(self):
        return self.type == 3 

    def getStatusName(self):
        status_map = dict( [('1',  u'通过申请'), ('2', u'待发放'), ('3', u'驳回申请'), ('4', u'打款异常,请稍等'), ('5', u'已发放')] ) 
        return status_map[ str(self.status) ] 

    def getType(self):
        status_map = dict([('1', u'微信企业打款'), ('2', u'微信红包'), ('3', u'支付宝')])
        return status_map[ str(self.type) ] 

    meta = {
        "ordering": ["-id"] 
    }

class MpQrUser2Url(db.Document):
    '''保存用户永久二维码url'''
    user = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    mp_url = db.StringField(max_length=200, verbose_name=u'用户的渠道URL')
    created_time = db.DateTimeField(default=datetime.datetime.now, verbose_name=u'添加时间')

class QrUser2MediaId(db.Document):
    '''推广二维码用户同MediaId映射表'''
    user = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    media_id = db.StringField(max_length=100, verbose_name=u'用户推广二维码MediaId')
    created_at = db.IntField(verbose_name=u'最后更新一次时间')
    type = db.IntField(default=0, verbose_name=u'类型')

class FansQueue(db.Document):
    user = db.ReferenceField(u'User', verbose_name=u'用户名', reverse_delete_rule=db.CASCADE)
    photo_url = db.StringField(max_length=200, default='', verbose_name=u'头像URL')
    qrimg_url = db.StringField(max_length=200, default='', verbose_name=u'个人微信二维码URL')
    qunimg_url = db.StringField(max_length=200, default='', verbose_name=u'微信群二维码URL') 

    nickname = db.StringField(max_length=200, default='', verbose_name=u'设置昵称')
    wechat = db.StringField(max_length=200, default='', verbose_name=u'设置微信')
    desc = db.StringField(max_length=300, default='', verbose_name=u'设置描述')

    qun_desc = db.StringField(max_length=300, default='', verbose_name=u'设置微信群描述') 

    province = db.StringField(max_length=50, default='', verbose_name=u'省份')
    city = db.StringField(max_length=50, default='', verbose_name=u'城市') 

    sex = db.StringField(max_length=4, default='', verbose_name=u'性别') 

    last_refresh_time = db.DateTimeField(default=datetime.datetime.now, verbose_name=u'刷新时间')

    is_Vip = db.BooleanField(default=True, verbose_name=u'是否是会员')
    meta = {
        "ordering": ['-last_refresh_time'] 
    }
    def getDiffTime(self):
        now = time.time()
        last_refresh_time = time.mktime(self.last_refresh_time.timetuple()) 
        seconds = now - last_refresh_time 
        if seconds <= 0:
            return u'刚刚' 
        mins = int(seconds / 60)  
        if mins <= 0:
            return u'刚刚' 
        elif mins < 60:
            return u'%s分钟前' % mins 
        else:
            pass 
        hours = int(mins / 60) 
        if hours < 24:
            return u'%s小时前' % hours 
        days = int(hours/24)
        return u'%s天前' % days 

class TipsLog(db.Document):
    '''微信提醒'''
    user = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    send_type = db.StringField(default=u'weixin', choices=[('weixin', u'微信'), ('sms', u'短信')])
    tip_type = db.StringField(max_length=20, verbose_name=u'提醒类型') 
    content_type = db.StringField(default="dict", max_length=20, verbose_name=u'内容类型')  
    data = db.StringField(verbose_name=u'消息内容')  
    msg_id = db.IntField(verbose_name=u'消息ID') 
    status = db.StringField(default='unsent', choices=[('unsent', u'未发送'), ('sent', u'已发送'), ('failure', u'发送失败')])
    retry_cnt = db.IntField(default=3, verbose_name=u'重试次数') 
    add_time = db.DateTimeField(default=datetime.datetime.now, verbose_name=u'添加时间') 
    sent_time = db.DateTimeField(verbose_name=u'发送时间') 
    remark = db.StringField(max_length=200, verbose_name=u'提示信息')  
    delay_time = db.IntField(default=0, verbose_name=u'延时delay_time发放')  

    meta = {
        "ordering": ["-id"] 
    }

class NewUserQueue(db.Document):
    user = db.ReferenceField('User', reverse_delete_rule=db.CASCADE, verbose_name=u'新用户')  
    add_time = db.DateTimeField(default=datetime.datetime.now, verbose_name=u'添加时间')  

class RedpackLog(db.Document):
    commission_ref = db.ReferenceField('ExtractionCommissionLog', verbose_name=u'提取佣金ID') 
    redpack_number = db.FloatField(default=0.0, verbose_name=u'红包金额')  
    mch_billno = db.StringField(default='', verbose_name=u'商户成交ID') 
    status = db.StringField(default='error', choices=[('error', u'失败'), ('success', u'成功')]) 
    remark = db.StringField(default='') 
    add_time = db.DateTimeField(default=datetime.datetime.now) 

class CommissionLogOfSubscribed(db.Document):
    '''只记录该用户的佣金是否分配''' 
    user = db.ReferenceField('User', reverse_delete_rule=db.CASCADE, verbose_name=u'该用户的佣金记录')
    add_time = db.DateTimeField(default=datetime.datetime.now)  


class Article(db.Document):
    title = db.StringField(default='', max_length=200, verbose_name=u'文章Title') 
    author = db.StringField(default=u'疯狂人脉说', verbose_name=u'发布作者')  
    content = db.StringField(default='', verbose_name=u'文章内容')  
    new = db.BooleanField(default=False, verbose_name=u'是否显示New标志')  
    hot = db.BooleanField(default=False, verbose_name=u'是否显示Hot标志')  
    add_time = db.DateTimeField(default=datetime.datetime.now, verbose_name=u'发布时间')
    display = db.BooleanField(default=False, verbose_name=u'是否显示')  
    meta = {
        "ordering": ["-id"] 
    }
