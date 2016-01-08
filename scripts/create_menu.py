#!/usr/bin/env python
#coding: utf8
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

def create_menu():
    with app.app_context():
        client = app.wxclient
        ret = client.create_menu(
{
    "button": [
        {
            "type": "view",
            "name": u"粉丝人脉",
            "url": "http://v.fkduobao.com/sc/m/list?fr=menu" 
            
        },
        {
            "type": "view",
            "name": u"发布二维码",
            "url": "http://v.fkduobao.com/sc/ucenter/upload?fr=menu" 
        },{
            "name": u"我的中心",
            "sub_button": [
                {
                    "type": "view",
                    "name": u"个人中心",
                    "url": "http://v.fkduobao.com/sc/ucenter/?fr=menu" 
                },{
                    "type": "click",
                    "name": u"我的分享二维码",
                    "key": "myqrcode"
                },{
                    "type": "view",
                    "name": u"购买VIP会员",
                    "url": "http://v.fkduobao.com/sc/shop/buy?fr=menu" 
                }
            ]
        }
    ]
}
            )
        print 'ret', ret

if __name__ == '__main__':
    create_menu()
    print 'Done!'

