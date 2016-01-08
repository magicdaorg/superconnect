#coding: utf8
import datetime
if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, models, notice, libwxpay
import time
import config
import random

def _sendMchPromotion(openid, partner_trade_no, number):
    '''number 单位是元 '''
    number = str(int(number*100)) #单位化成分
    handler = libwxpay.MchPromotion_pub()
    handler.setParameter('partner_trade_no', partner_trade_no)
    handler.setParameter('openid', openid)
    handler.setParameter('check_name', 'NO_CHECK')
    handler.setParameter('amount', number)
    handler.setParameter('desc', '感谢您支持疯狂人脉说，继续推广!')
    handler.setParameter('spbill_create_ip', '58.96.179.124')

    ret = handler.getResult()
    return ret

def sendMchCommission(user, number):
    mch_billno = "%s%s%s" % (config.SuperConnect.WXMCH_ID, datetime.datetime.now().strftime('%Y%M%d'), random.randint(1000000000, 9999999999))
    openid = user.openid
    number = number
    ret = _sendMchPromotion(openid, mch_billno, number)
    if ret["return_code"] == "SUCCESS":
        if ret["result_code"] == "SUCCESS":
            is_success = True
            remark = u'发放成功'
            status = 'success'

            '''分享推广二维码，别人关注立即发放1毛钱''' 
            notice.redpack_sent_notice(user, number) 
        else:
            is_success = False
            status = ret['err_code']
            remark = ret["err_code_des"]
            '''重要'''
            if status == 'SYSTEMERROR':
                print status
    else:
        is_success = False
        status = 'error'
        remark = ret["return_msg"] 
if __name__=='__main__':
    with app.app_context():
        user = models.User.objects(openid="obmdTw4eo6ACVP5W8zvYyyhpuODA").first()  
        sendMchCommission(user, 0.1) 
