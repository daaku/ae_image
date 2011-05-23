# -*- coding: utf-8 -*-
"""
Unit tests for ae_image.db_property.

"""
# pylint: disable=C0111

from ae_image_test import BaseTestCase
from google.appengine.ext import db
import ae_image.db_property
import ae_image.core


class TestAlbum(db.Model):
    name = db.StringProperty()
    images = ae_image.Property([
        ae_image.Style('thumb', size=50, quality=75),
        ae_image.Style('medium', size=300, quality=85)])


class CollectionPropertyTestCase(BaseTestCase):
    def test_default_property_value(self):
        album = TestAlbum(name='test')
        self.assertTrue(
            isinstance(album.images, ae_image.core.Collection),
            'Expect default value to be a Collection instance.')
