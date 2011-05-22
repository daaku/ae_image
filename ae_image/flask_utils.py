# -*- coding: utf-8 -*-
"""
Helpers to handle extracting blob keys and content types from a Flask request
and update an ImageCollection.

"""


_ALLOWED_TYPES = ['gif', 'jpeg', 'png']


def append_from_request(collection, field_name, allowed_types=None):
    """
    Appends a new image to the collection from the current Flask request.

    """

    if not allowed_types:
        allowed_types = _ALLOWED_TYPES
