#encoding: utf8 
from app import app
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple

_app = DispatcherMiddleware(
        app, {
        }
    )

if __name__=='__main__':
    run_simple('0.0.0.0', 2048, _app, use_reloader=False, use_debugger=True, threaded=True)
