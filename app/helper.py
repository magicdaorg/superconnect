#coding: utf8
import PIL
from PIL import Image
from app import app, models
from cStringIO import StringIO
import zbar 
import uuid 
import traceback 
import imghdr 
ALLOWED_EXTENSIONS = set(['gif', 'png', 'jpg', 'jpeg', 'bmp'])

def allowed_file(image):
    ext = imghdr.what(image) 
    if not ext:
        return False 
    return ext.lower() in ALLOWED_EXTENSIONS 

def gen_file_name(filename):
    """
    If file was exist already, rename it and return a new name
    """

    i = 1
    while os.path.exists(os.path.join(app.config['UPLOAD_FANS_DIR'], filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i = i + 1

    return filename


def create_thumbnai(save_filename, image):
    basewidth = 80
    img = Image.open(image)
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
    img.save(save_filename)

def create_image(save_filename, image):
    img = Image.open(image)
    img.save(save_filename)

def handle_head_image(user, image):
    try:
        image_id = uuid.uuid4().hex  
        thumbnail_filename = '%s/%s_t.jpeg' % (app.config['THUMBNAIL_FOLDER'].rstrip('/'), image_id)

        create_thumbnai(thumbnail_filename, image)

        url = '/upload/thumbnail/%s_t.jpeg' % image_id   
        return {'ret': 0, "data": {'url': url}}
    except Exception, e:
        error = str(e)
        return {'ret': -1, "error": error}

def qrImage2Data(image):
    scanner = zbar.ImageScanner()   
    scanner.parse_config('enable')   
    width, height = image.size  
    raw = image.tobytes()  
    image = zbar.Image(width, height, 'Y800', raw) 

    scanner.scan(image) 
    data = '' 
    for i in image.symbols:
        if i.type == zbar.Symbol.QRCODE: 
            data = i.data 
    del(image) 
    return data 

def handle_qr_image(user, image):
    try:
        image_id = uuid.uuid4().hex 
        origin_filename = '%s/%s_q.jpeg' % (app.config['UPLOAD_FANS_DIR'].rstrip('/'), image_id)

        i = Image.open(image).convert('L') 
        data = qrImage2Data(i) 
        if not data:
            error = u'对不起！您上传的图片中不包含任何二维码哟！' 
            return {'ret': -1, 'error': error} 

        if data.startswith('http://weixin.qq.com/q'):
            error = u'警告！您上传的是公众号二维码，请上传您自己的个人二维码！' 
            return {'ret': -2, 'error': error} 

        if not data.startswith('http://weixin.qq.com/r'):
            error = u'警告！请上传您个人的微信二维码！'
            return {'ret': -3, 'error': error} 

        create_image(origin_filename, image)
        url = '/upload/fans/%s_q.jpeg' % image_id  
        return {'ret': 0, "data": {'url': url}}
    except Exception, e:
        error = str(e)
        return {'ret': -4, "error": error}

def handle_qun_image(user, image):
    try:
        image_id = uuid.uuid4().hex 
        origin_filename = '%s/%s_qun.jpeg' % (app.config['UPLOAD_FANS_DIR'].rstrip('/'), image_id)

        i = Image.open(image).convert('L')
        data = qrImage2Data(i)
        if not data:
            error = u'对不起！您上传的图片中不包含任何二维码哟！'
            return {'ret': -1, 'error': error}

        if data.startswith('http://weixin.qq.com/q'):
            error = u'警告！您上传的是公众号二维码，请上传您的微信群二维码！'
            return {'ret': -2, 'error': error}

        if data.startswith('http://weixin.qq.com/r'):
            error = u'警告！您上传的是您个人微信二维码，请上传您的微信群二维码！'
            return {'ret': -3, 'error': error} 
        
        if not data.startswith('http://weixin.qq.com/g'):
            error = u'警告！请上传您的微信群二维码！'
            return {'ret': -4, 'error': error} 

        create_image(origin_filename, image) 
        url = '/upload/fans/%s_qun.jpeg' % image_id 
        return {'ret': 0, "data": {'url': url}} 
    except Exception, e:
        print traceback.print_exc() 
        error = str(e)
        return {'ret': -4, "error": error} 
