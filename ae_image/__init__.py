# -*- coding: utf-8 -*-
"""
ae_image provides an abstraction for use with Google AppEngine to manage a
collection of images stored in a ``db.Model`` and efficiently serve them.

"""

from ae_image.core import Style, Collection, UrlNotFound
from ae_image.db_property import Property
