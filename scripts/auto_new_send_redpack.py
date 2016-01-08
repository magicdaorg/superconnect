#!/usr/bin/env python
#coding: utf8
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime

from app import models, notice, libwxpay  
import time
from app import app as appinstance
import config 
import random 
import threading 

mutex = threading.Lock()

waiting_to_sends_logs = [] 

def sendRedpack(openid, mch_billno, number):
    '''
        number: 单位是元  
    '''
    number = str(int(number * 100)) #单位成分
    handler = libwxpay.SendRedPack_pub() 
    '''商户订单号''' 
    handler.setParameter('mch_billno', mch_billno) 
    handler.setParameter('wxappid', config.SuperConnect.WXAPP_ID) 
    handler.setParameter('nick_name', config.SuperConnect.WXAPP_NAME) 
    handler.setParameter('send_name', config.SuperConnect.WXAPP_NAME) 
    handler.setParameter('re_openid', openid) 
    handler.setParameter('total_amount', number) 
    handler.setParameter('min_value', number) 
    handler.setParameter('max_value', number) 
    handler.setParameter('total_num', '1') 
    handler.setParameter('wishing', '感谢您支持疯狂人脉说，继续分享，继续赚钱!') 
    handler.setParameter('client_ip', '121.41.24.86') 
    handler.setParameter('act_name', '分享得红包') 
    handler.setParameter('remark', '感谢您信任我们!') 

    ret = handler.getResult() 
    return ret 

def sendMchPromotion(openid, partner_trade_no, number):
    '''number 单位是元 ''' 
    number = str(int(number*100)) #单位化成分 
    handler = libwxpay.MchPromotion_pub() 
    handler.setParameter('partner_trade_no', partner_trade_no)  
    handler.setParameter('openid', openid)
    handler.setParameter('check_name', 'NO_CHECK') 
    handler.setParameter('amount', number) 
    handler.setParameter('desc', '感谢您支持疯狂人脉说，您的佣金已经发放!')  
    handler.setParameter('spbill_create_ip', '121.41.24.86') 

    ret = handler.getResult() 
    return ret 

def recheckMchBillNo(mch_billno):
    pass 

def _sendRedpack():
    global waiting_to_sends_logs
    
    with appinstance.app_context():
        number_per_redpack = 200 
        wxmch_id = config.SuperConnect.WXMCH_ID 
        is_break = False
        while 1:
            mutex.acquire() 
            try:
                i = waiting_to_sends_logs.pop() 
            except IndexError:
                is_break = True 
            mutex.release() 

            if is_break:
                break 
            print i.user, i.add_time, i.number   

            is_success = True 
            now = datetime.datetime.now() 
            if i.isWechatRedpack():
                '''微信红包支付''' 
                i.update(set__remark=u'微信支付') 

                try:
                    sent_redpack_number = models.RedpackLog.objects(commission_ref=i, status='success').sum('redpack_number')
                except:
                    sent_redpack_number = 0.0 
                left_redpack_number = i.number - sent_redpack_number  

                while left_redpack_number > 0:
                    time.sleep(1) 
                    mch_billno = "%s%s%s" % (wxmch_id, datetime.datetime.now().strftime('%Y%M%d'), random.randint(1000000000, 9999999999))     
                    if left_redpack_number >= number_per_redpack:
                        number = number_per_redpack 
                    else:
                        number = left_redpack_number 
                    left_redpack_number -= number  
                    ret = sendRedpack(i.user.openid, mch_billno, number)     
                    if ret['return_code'] == 'SUCCESS': 
                        if ret['result_code'] == 'SUCCESS':
                            status = 'success' 
                            remark = u'发放成功' 
                        else:
                            status = ret['err_code'] 
                            remark = ret['err_code_des'] 
                            '''重要!!!'''
                            if status == 'SYSTEMERROR':
                                '''需要根据单号重新查询发放结果''' 
                                models.RedpackLog(commission_ref=i, redpack_number=number, mch_billno=mch_billno, status=status, remark=remark).save()         
                                recheckMchBillNo(mch_billno) 
                                continue 
                    else:
                        status = 'error' 
                        remark = ret['return_msg']   
                    if status != 'success':
                        is_success = False 
                    models.RedpackLog(commission_ref=i, redpack_number=number, mch_billno=mch_billno, status=status, remark=remark).save()         
            elif i.isMch():
                '''微信企业打款方式''' 
                i.update(set__remark=u'微信企业打款') 
                mch_billno = "%s%s%s" % (wxmch_id, datetime.datetime.now().strftime('%Y%M%d'), random.randint(1000000000, 9999999999))     
                openid = i.user.openid 
                number = i.number 
                ret = sendMchPromotion(openid, mch_billno, number) 
                if ret["return_code"] == "SUCCESS":
                    if ret["result_code"] == "SUCCESS":
                        is_success = True 
                        remark = u'发放成功' 
                        status = 'success' 
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
                models.RedpackLog(commission_ref=i, redpack_number=number, mch_billno=mch_billno, status=status, remark=remark).save() 
            elif i.isZhifubao():
                print u'支付宝支付' 
            else:
                pass 

            if is_success:
                '''发放成功''' 
                i.update(set__status=5) 
                i.update(set__sent_time=now) 

                '''发送提现成功通知''' 
                notice.redpack_sent_notice(i.user, i.number) 
            else:
                '''打款失败''' 
                i.update(set__status=4) 

def autoSendRedpack(wxmch_id=config.SuperConnect.WXMCH_ID, number_per_redpack=200):
    global waiting_to_sends_logs 
    with appinstance.app_context():
        break_flag = False
        while True:
            if break_flag:
                break 
            waiting_to_sends_logs = list( models.ExtractionCommissionLog.objects(status=1)[:20] )#通过申请 
            if len(waiting_to_sends_logs) <= 0:
                print "Sleeping %s seconds...." % 5 
                time.sleep(5) 

            _t = []
            for i in xrange(5):
                _t.append(threading.Thread( target = _sendRedpack )) 
            for t in _t:
                t.daemon = True
                t.start() 

            for t in _t:
                t.join()

if __name__ == '__main__':
    autoSendRedpack() 
    #with appinstance.app_context():
    #    openid = 'ou1zRt63h4mEawJNSxdGqbDq0FUo' 
    #    mch_billno = "%s%s%s" % (config.SuperConnect.WXMCH_ID, datetime.datetime.now().strftime('%Y%M%d'), random.randint(1000000000, 9999999999))     
    #    ret = sendMchPromotion(openid, mch_billno, 1) 
    #    print ret 
    #    if ret["return_code"] == "SUCCESS":
    #        if ret["result_code"] == "SUCCESS":
    #            print u'发放成功'
    #        else:
    #            print "%s %s" % (ret["err_code"], ret["err_code_des"]) 
    #    else:
    #        print ret["return_msg"] 
