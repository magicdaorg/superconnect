#encoding: utf8 
from sys import argv, exit  
import zbar 
from PIL import Image 


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

if __name__=="__main__":
    if len(argv) < 2:
        print "Usage: %s qr_image" % argv[0] 
        exit(1) 
    filename = argv[1]
    image = Image.open(filename).convert("L")  

    data = qrImage2Data(image) 
    print data 
