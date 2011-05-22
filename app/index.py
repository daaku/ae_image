# -*- coding: utf-8 -*-
"""
Example application for ae_image.

"""

import sys
from os import path, environ
sys.path[1:1] = [path.abspath(path.dirname(__file__) + '/lib')]

from ae_image.flask_utils import append_from_request
from flask import Flask, render_template, request, url_for, redirect
from wsgiref.handlers import CGIHandler
import ae_image
import google.appengine.ext.blobstore as blobstore
import logging

app = Flask(__name__)


@app.route('/')
def home():
    upload_url = blobstore.create_upload_url(url_for('upload'))
    return render_template('home.html', upload_url=upload_url)


@app.route('/upload', methods=['POST'])
def upload():
    logging.info('request.files: ' + str(request.files))
    collection = ae_image.Collection([
        ae_image.Style('thumb', size=50)])
    append_from_request(collection, 'images')
    logging.info(collection)
    response = redirect(url_for('home'))
    response.data = ''
    return response


if __name__ == '__main__':
    if environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
        import werkzeug_debugger_appengine
        app.debug = True
        app = werkzeug_debugger_appengine.get_debugged_app(app)
    CGIHandler().run(app)
