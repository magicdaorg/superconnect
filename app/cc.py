#encoding: utf8
import models
from mongoengine import Q
from flask import current_app
from app import models
from app import notice

def updateUserCommission(user, order, commission):
    models.CommissionLog(user=user, order=order, commission=commission).save()
    '''修改佣金数'''
    user.update(inc__commission=commission)
    user.update(inc__with_commission=commission)
    notice.userNewCommission(user, order.user.nickname, order.fee, commission)


def distributeCommissionForFriend(order):
    '''三级分销分润'''
    buyer = order.user
    promo_upline = buyer.getMyPromo()

    fee = order.fee
    friend_level = 1
    while promo_upline and not promo_upline.isVirtualUser() and friend_level <= 3:
        if friend_level == 1:
            commission_rate = current_app.config['FRIEND1']
        elif friend_level == 2:
            commission_rate = current_app.config['FRIEND2']
        elif friend_level == 3:
            commission_rate = current_app.config['FRIEND3']
        else:
            commission_rate = 0

        friend_level += 1
        updateUserCommission(promo_upline, order, fee*commission_rate)
        promo_upline = promo_upline.getMyPromo()

