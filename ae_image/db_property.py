# -*- coding: utf-8 -*-
"""
Provides a property that represents a collection of images uploaded using the
blobstore API, and served in various sizes via get_serving_url for maximum
client side performance. It can also be instructed to force served URLs to be
in JPEG format of a certain quality for controlling file sizes accepting some
lossy conversion.

"""

import pickle
from google.appengine.ext import db
from ae_image.core import Collection


class Property(db.Property):
    """A property to store a Collection."""

    data_type = Collection

    def __init__(self, styles, **kwargs):
        super(Property, self).__init__(**kwargs)
        self.styles = styles

    def default_value(self):
        return Collection(self.styles)

    def empty(self, value):
        return not value.images

    def validate(self, value):
        if value is not None and not isinstance(value, Collection):
            raise db.BadValueError(
                'Property %s must be a Collection.' % self.name)
        return super(Property, self).validate(value)

    def get_value_for_datastore(self, model_instance):
        result = super(Property, self).get_value_for_datastore(model_instance)
        result = pickle.dumps(result)
        return db.Blob(result)

    def make_value_from_datastore(self, value):
        value = pickle.loads(str(value))
        if not value:
            value = self.default_value()
        value.styles = self.styles
        return super(Property, self).make_value_from_datastore(value)
