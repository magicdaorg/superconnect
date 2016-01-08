#coding: utf8
import os
import datetime 

def get_path(rpath):
    LOCAL_DIR = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(LOCAL_DIR, rpath))

class SuperConnect(object):
    SECRET_KEY =  '6a00dc89f2d73cd49e472b34f621ab27'
    WXAPP_ID = 'wx43dd95469ffc2b46' 
    WXAPP_SECRET = '21df40b8fc6529601f9370c00cdd0462' 
    WXAPP_NAME = '疯狂人脉说'
    DOMAIN = 'http://v.fkduobao.com' 

    SERVICE_CONTACT = ''

    WEROBOT_ROLE = '/sc/robot'
    WEROBOT_TOKEN = 'superconnect'

    WXMCH_SSLKEY_PATH = get_path('app/certs/apiclient_key.pem')
    WXMCH_SSLCERT_PATH = get_path('app/certs/apiclient_cert.pem')
    WXMCH_KEY = 'magichudogecoinwumaihenyanzhong1' 
    WXMCH_ID = '1303341801'
    CURL_TIMEOUT = 30
    HTTP_CLIENT = 'curl'

    PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=24)  

    MONGODB_SETTINGS = {
        'HOST': '127.0.0.1',
        'DB': 'superconnect',
    }

    UPLOAD_DIR = '/data/superconnect/upload'
    UPLOAD_FANS_DIR = '/data/superconnect/upload/fans'
    THUMBNAIL_FOLDER = '/data/superconnect/upload/thumbnail' 

    DEBUG = True
    #三级分销系统提成比例
    FRIEND1 = 0.3
    FRIEND2 = 0.1
    FRIEND3 = 0.05 
