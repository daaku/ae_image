# -*- coding: utf-8 -*-
"""
Example application for ae_image.

"""

import sys
from os import path, environ
sys.path.append(path.abspath(path.dirname(__file__) + '/lib'))

from flask import Flask
from wsgiref.handlers import CGIHandler

app = Flask(__name__)


@app.route('/')
def home():
    return "Hello World!"

if __name__ == '__main__':
    if environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
        import werkzeug_debugger_appengine
        app.debug = True
        app = werkzeug_debugger_appengine.get_debugged_app(app)
    CGIHandler().run(app)
