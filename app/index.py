# -*- coding: utf-8 -*-
"""
Example application for ae_image.

"""

import sys
import os
sys.path[1:1] = [os.path.abspath(os.path.dirname(__file__) + '/lib')]

from ae_image.flask_utils import append_from_request
from flask import Flask, render_template, request, url_for, redirect
from google.appengine.ext import db, blobstore
from werkzeug.urls import url_decode
from wsgiref.handlers import CGIHandler
import ae_image

app = Flask(__name__)


class MethodRewriteMiddleware(object):
    """
    Adds support for HTTP method overriding using the _method query parameter.
    Note, it **must** be in the query, post data is not looked at.

    """

    def __init__(self, application):
        self.app = application

    def __call__(self, environ, start_response):
        if '_method' in environ.get('QUERY_STRING', ''):
            args = url_decode(environ['QUERY_STRING'])
            method = args.get('_method')
            if method:
                method = method.encode('ascii', 'replace')
                environ['REQUEST_METHOD'] = method
        return self.app(environ, start_response)


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


@app.route('/collection/<name>/<key>')
def image(name, key):
    """Shows an image from a collection."""

    return render_template('image.html', key=key,
        collection=NamedCollections.get_named(name))


@app.route('/collection/<name>/<key>', methods=['DELETE'])
def remove_image(name, key):
    """Removes a single image from a collection."""

    collection = NamedCollections.get_named(name)
    collection.images.remove(key)
    collection.save()
    return redirect(url_for('home'))


if __name__ == '__main__':
    if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
        import werkzeug_debugger_appengine
        app.debug = True
        app = werkzeug_debugger_appengine.get_debugged_app(app)
    app = MethodRewriteMiddleware(app)
    CGIHandler().run(app)
