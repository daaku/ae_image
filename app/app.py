# -*- coding: utf-8 -*-
"""
AppEngine bootstrap for ae_image_app.

"""

import sys
import os
sys.path[1:1] = [os.path.abspath(os.path.dirname(__file__) + '/lib')]

from ae_image_app import app
from wsgiref.handlers import CGIHandler


if __name__ == '__main__':
    if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
        import werkzeug_debugger_appengine
        app.debug = True
        app = werkzeug_debugger_appengine.get_debugged_app(app)
    CGIHandler().run(app)
