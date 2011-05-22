# -*- coding: utf-8 -*-
"""
Example application for ae_image.

"""

import sys
from os import path, environ
sys.path[1:1] = [path.abspath(path.dirname(__file__) + '/lib')]

from ae_image.flask_utils import append_from_request
from flask import Flask, render_template, request, url_for, redirect
from google.appengine.ext import db, blobstore
from wsgiref.handlers import CGIHandler
import ae_image

app = Flask(__name__)


class NamedCollections(db.Model):
    """A simple named collection model to demonstrate the use of ae_image."""
    name = db.StringProperty()
    images = ae_image.Property([
        ae_image.Style('thumb', size=50, quality=75),
        ae_image.Style('medium', size=300, crop=True)])

    @classmethod
    def get_named(cls, name):
        """Get or insert a named collection."""
        return cls.get_or_insert(name, name=name)


@app.route('/')
def home():
    """The main landing page."""
    return render_template('home.html',
        upload_url=blobstore.create_upload_url(url_for('upload')),
        collections=list(NamedCollections.all()))


@app.route('/upload', methods=['POST'])
def upload():
    """Handles blobstore uploads and adds images to a named collection."""
    collection = NamedCollections.get_named(request.form['name'])
    append_from_request(collection.images, 'images')
    collection.save()
    response = redirect(url_for('home'))
    response.data = ''
    return response


if __name__ == '__main__':
    if environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
        import werkzeug_debugger_appengine
        app.debug = True
        app = werkzeug_debugger_appengine.get_debugged_app(app)
    CGIHandler().run(app)
