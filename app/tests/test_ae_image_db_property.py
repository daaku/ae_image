# -*- coding: utf-8 -*-
"""
Unit tests for ae_image.db_property.

"""
# pylint: disable=C0111

from ae_image_test import BaseTestCase
from google.appengine.ext import blobstore, db
import ae_image.db_property
import ae_image.core


class TestAlbum(db.Model):
    images = ae_image.Property([
        ae_image.Style('thumb', size=50, quality=75),
        ae_image.Style('medium', size=300, quality=85)])


class CollectionPropertyTestCase(BaseTestCase):
    def test_default_property_value(self):
        album = TestAlbum()
        self.assertTrue(
            isinstance(album.images, ae_image.core.Collection),
            'Expect default value to be a Collection instance.')

    def test_store_and_restore(self):
        blob_key = self.make_blob('image/jpeg', 'dummy')
        album_key = 'test_store_and_restore'
        album = TestAlbum(key_name=album_key)
        album.images.append_from_blob_info(blobstore.BlobInfo.get(blob_key))
        album.save()

        album = TestAlbum.get_by_key_name(album_key)
        self.assertTrue(
            album.images.get_url('thumb', blob_key), 'Expect URL back.')

    def test_adding_new_style(self):
        class TestAlbumAlt(db.Model):
            images = ae_image.Property([
                ae_image.Style('thumb', size=50, quality=75),
                ae_image.Style('medium', size=300, quality=85)])

        blob_key = self.make_blob('image/jpeg', 'dummy')
        album_key = 'test_adding_new_style'
        album = TestAlbumAlt(key_name=album_key)
        album.images.append_from_blob_info(blobstore.BlobInfo.get(blob_key))
        album.save()

        self.assertRaises(ae_image.core.UnknownStyle, album.images.get_url,
            'big', blob_key)

        TestAlbumAlt.images.styles.append(
            ae_image.Style('big', size=600, quality=95))

        album = TestAlbumAlt.get_by_key_name(album_key)
        self.assertRaises(ae_image.core.UrlNotFound, album.images.get_url,
            'big', blob_key)

        self.assertTrue(album.images.generate_urls(),
            'Expect to generate some URLs.')
        self.assertTrue(
            album.images.get_url('big', blob_key), 'Expect URL back.')

    def test_adding_property_to_existing_model(self):
        class TestAlbumAlt(db.Model):
            pass

        album_key = 'test_adding_property_to_existing_model'
        album = TestAlbumAlt(key_name=album_key)
        album.save()

        class TestAlbumAlt(db.Model):
            images = ae_image.Property([
                ae_image.Style('thumb', size=50, quality=75),
                ae_image.Style('medium', size=300, quality=85)])

        blob_key = self.make_blob('image/jpeg', 'dummy')
        album = TestAlbumAlt.get_by_key_name(album_key)
        album.images.append_from_blob_info(blobstore.BlobInfo.get(blob_key))
        album.save()
        self.assertTrue(
            album.images.get_url('thumb', blob_key), 'Expect URL back.')
