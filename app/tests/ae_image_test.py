# -*- coding: utf-8 -*-
"""
Helpers for unit tests for ae_image.

"""

from __future__ import with_statement
from flask import Flask
from flaskext.testing import TestCase
from google.appengine.api import files


class BaseTestCase(TestCase):
    """Base TestCase for ae_image tests."""

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    @staticmethod
    def make_blob(content_type, data):
        """Writes a blob and returns the blob_key of the created blob."""

        file_name = files.blobstore.create(mime_type=content_type)
        with files.open(file_name, 'a') as blob_file:
            blob_file.write(data)
        files.finalize(file_name)
        return files.blobstore.get_blob_key(file_name)
