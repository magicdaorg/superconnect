#coding: utf8
from cStringIO import StringIO
from PIL import Image, ImageFile
from PIL import ImageDraw
from PIL import ImageFont
import qrcode
from app import models, app
import os
import urllib2

wxclient = app.wxclient

FONT_simhei = ImageFont.truetype(os.path.join(os.path.dirname(__file__), "simhei.ttf"), 28)
ImageFile.MAXBLOCK = 2**20

def makeUrlQrcode(user, url, (name_x, name_y), (head_x, head_y, head_size), (qr_x, qr_y, qr_size), template_img_path, img_save_path):
    qr = qrcode.QRCode(version=2, box_size=10, border=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(url)
    qr_img = qr.make_image()
    qr_img = qr_img.resize((qr_size, qr_size), Image.BILINEAR)

    url = user.headimgurl[:-1] + '132'
    req = urllib2.Request(url, headers={'User-Agent': ''})
    head_file = StringIO(urllib2.urlopen(req).read())
    head_img = Image.open(head_file)
    head_img = head_img.resize((head_size, head_size), Image.BILINEAR)

    main = Image.open( template_img_path )
    main.paste(qr_img, (qr_x, qr_y))
    main.paste(head_img, (head_x, head_y))
    draw = ImageDraw.Draw(main)
    draw.text((name_x, name_y), user.nickname, font=FONT_simhei, fill=(255,86,57))

    out_file = "%s/%s.jpeg" % ( img_save_path.rstrip("/"), user.id )
    main.save(out_file, 'JPEG', optimize=True, quality=90, progressive=True)
    return out_file

def __getUserMpUrl(user):
    ref = models.MpQrUser2Url.objects(user=user).first()
    if not ref:
        '''获取带渠道的URL'''
        params = {"action_name": "QR_LIMIT_STR_SCENE", "action_info": {"scene": {"scene_str": "%s" % (user.id)}}}
        ret = wxclient.create_qrcode(**params)
        try:
            url = ret['url']
            '''将该用户的渠道URL保存到数据库中'''
            models.MpQrUser2Url(user=user, mp_url=url).save()
            return url
        except:
            print ret
            return None
    else:
        return ref.mp_url

def getLocalQrImagePath(user, type=0):
    if type == 0:
        localPath = "/data/superconnect/qrchannelimgs/%s.jpeg" % user.id
    else:
        return None

    if os.path.exists(localPath):
        return localPath
    mp_url = __getUserMpUrl(user)
    if not mp_url:
        return None
    head_pos = (28, 38, 134)
    name_pos = (268, 50)
    qr_pos = (173, 366, 254)
    template_img_path = "/opt/xxoo/superconnect/app/www/img/template_qr_black.jpg"
    img_save_path = "/data/superconnect/qrchannelimgs/"
    localPath = makeUrlQrcode(user, mp_url, name_pos, head_pos, qr_pos, template_img_path, img_save_path)
    return localPath

def getWwwQrImagePath(user, type=0):
    path = getLocalQrImagePath(user, type) 
    mediaId = os.path.basename(path) 
    return "/qrchannelimgs/%s" % mediaId 
