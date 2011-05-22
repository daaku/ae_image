# -*- coding: utf-8 -*-
"""
Helpers to handle extracting blob keys and content types from a Flask request
and update an ImageCollection.

"""

from flask import current_app as app, request
from google.appengine.ext.blobstore import BlobInfo
from werkzeug.http import parse_options_header


def append_from_request(collection, field_name):
    """
    Appends new image(s) to the collection from the current Flask request.
    Returns the count of number of blobs that were added to the collection.

    """

    blob_keys = []
    for file_info in request.files.getlist(field_name):
        file_header = parse_options_header(file_info.headers['Content-Type'])
        blob_keys.append(file_header[1]['blob-key'])
    map(collection.append_from_blob_info,  BlobInfo.get(blob_keys))
    return len(blob_keys)
