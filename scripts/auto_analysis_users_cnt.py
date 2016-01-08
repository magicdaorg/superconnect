#coding: utf8
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from app import app, models, uc
import traceback 

def all():
    with app.app_context():
        break_flag = False
        while True:
            if break_flag:
                break
            users = models.User.objects()
            for u in users:
                try:
                    '''开始统计'''
                    friends1, friends2, friends3 = uc.get3DownlineFriend(u, 3)

                    friends1_cnt = len(friends1)
                    friends2_cnt = len(friends2)
                    friends3_cnt = len(friends3)

                    friends_cnt = friends1_cnt + friends2_cnt + friends3_cnt
                    u.update(set__friends_cnt=friends_cnt)
                    u.update(set__friends1_cnt=friends1_cnt)
                    u.update(set__friends2_cnt=friends2_cnt)
                    u.update(set__friends3_cnt=friends3_cnt)
                    print "%s Done" % u
                    #清理内存
                    del friends1[:] 
                    del friends2[:]
                    del friends3[:] 
                except:
                    print traceback.print_exc() 
            print "Sleeping %s" % (60*30) 
            time.sleep(60*30)

if __name__=='__main__':
    import sys
    if len(sys.argv) == 2:
        cmd = sys.argv[1]
        if cmd not in ['all', 'part']:
            cmd = 'all'
    else:
        cmd = "all"
    print "Handle using cmd %s" % cmd
    if cmd == "all":
        all()
    elif cmd == 'part':
        part()
