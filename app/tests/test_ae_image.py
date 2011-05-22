# -*- coding: utf-8 -*-
"""
Unit tests for ae_image.

"""
# pylint: disable=C0111,R0201

from __future__ import with_statement
from flask import Flask
from flaskext.testing import TestCase
from google.appengine.api import files
from google.appengine.ext.blobstore import BlobInfo
import ae_image.core


class BaseTestCase(TestCase):
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


class StyleTestCase(BaseTestCase):
    def test_hash_equal_for_no_format_and_quality(self):
        style1 = ae_image.core.Style('style1')
        style2 = ae_image.core.Style('style2')
        assert hash(style1) == hash(style2)

    def test_hash_equal_for_same_format(self):
        style1 = ae_image.core.Style('style1', format='jpeg')
        style2 = ae_image.core.Style('style2', format='jpeg')
        assert hash(style1) == hash(style2)

    def test_hash_equal_for_different_size(self):
        style1 = ae_image.core.Style('style1', size=42, format='jpeg')
        style2 = ae_image.core.Style('style2', size=42, format='jpeg')
        assert hash(style1) == hash(style2)

    def test_hash_equal_for_different_crop(self):
        style1 = ae_image.core.Style('style1', size=42, format='jpeg')
        style2 = ae_image.core.Style(
            'style2', size=42, crop=True, format='jpeg')
        assert hash(style1) == hash(style2)

    def test_hash_not_equal_for_different_format(self):
        style1 = ae_image.core.Style('style1', format='jpeg')
        style2 = ae_image.core.Style('style2', format='gif')
        assert hash(style1) != hash(style2)

    def test_hash_not_equal_for_different_quality(self):
        style1 = ae_image.core.Style('style1', format='jpeg', quality=70)
        style2 = ae_image.core.Style('style2', format='jpeg', quality=80)
        assert hash(style1) != hash(style2)


class ImageTestCase(BaseTestCase):
    def test_empty_image_has_original_url(self):
        image = ae_image.core.Image('abc', 'jpeg')
        assert len(image.blobs) == 1
        assert image.get_url(ae_image.core.Style('original'))
        assert image.get_url(ae_image.core.Style('name_doesnt_matter'))
        assert image.get_url(ae_image.core.Style('original', size=10))
        assert image.get_url(
            ae_image.core.Style('original', size=10, crop=True))

    def test_image_with_existing_blobs(self):
        image1 = ae_image.core.Image('abc', 'jpeg')
        image1.generate_url(ae_image.core.Style('another', format='gif'))

        image2 = ae_image.core.Image('abc', 'jpeg', image1.blobs)
        assert len(image2.blobs) == 2

    def test_generate_url_for_new_format(self):
        image = ae_image.core.Image('abc', 'jpeg')
        image.generate_url(ae_image.core.Style('another', format='gif'))
        assert len(image.blobs) == 2
        assert image.get_url(ae_image.core.Style('another', format='gif'))

    def test_raise_on_missing_url(self):
        image = ae_image.core.Image('abc', 'jpeg')
        try:
            assert not image.get_url(
                ae_image.core.Style('another', format='gif'))
        except ae_image.core.UrlNotFound, ex:
            assert repr(ex) == (
                u'URL for blob_key "abc" for style "another" was not found.')

    def test_remove_image_with_only_original_blob(self):
        content_type = 'image/jpeg'
        blob_key = self.make_blob(content_type, 'dummy')
        assert BlobInfo.get(blob_key)
        image = ae_image.core.Image(blob_key, content_type)
        image.remove()
        assert not BlobInfo.get(blob_key)

    def test_remove_image_with_multiple_blobs(self):
        pass


class ImageCollectionTestCase(BaseTestCase):
    def test_empty_image_collection(self):
        collection = ae_image.core.Collection([])
        assert len(collection.images) == 0

    def test_raise_on_unknown_style(self):
        blob_key = 'abc'
        collection = ae_image.core.Collection(
            [ae_image.core.Style('big', 500)])
        collection.append(blob_key, 'jpeg')
        try:
            assert not collection.get_url(blob_key, 'small')
        except ae_image.core.UnknownStyle, ex:
            assert repr(ex) == u'Unknown style "small" requested.'

    def test_raise_on_unknown_image(self):
        collection = ae_image.core.Collection(
            [ae_image.core.Style('big', 500)])
        collection.append('abc', 'jpeg')
        try:
            assert not collection.get_url('def', 'big')
        except ae_image.core.UnknownImage, ex:
            assert repr(ex) == u'Unknown image blob_key "def" requested.'

    def test_get_valid_single_url(self):
        blob_key = 'abc'
        collection = ae_image.core.Collection(
            [ae_image.core.Style('big', 500)])
        collection.append(blob_key, 'jpeg')
        assert collection.get_url(blob_key, 'big')

    def test_get_valid_ordered_urls_for_all_images(self):
        blob_key1 = 'abc'
        blob_key2 = 'def'
        collection = ae_image.core.Collection(
            [ae_image.core.Style('big', 500)])
        collection.append(blob_key1, 'jpeg')
        collection.append(blob_key2, 'jpeg')
        urls = list(collection.get_urls('big'))
        assert len(urls) == 2
        assert urls[0] == collection.get_url(blob_key1, 'big')
        assert urls[1] == collection.get_url(blob_key2, 'big')

    def test_generate_urls_for_new_style(self):
        blob_key = 'abc'
        collection = ae_image.core.Collection(
            [ae_image.core.Style('big', 500)])
        collection.append(blob_key, 'jpeg')
        assert not collection.generate_urls()
        collection.styles['low'] = ae_image.core.Style('low', format='jpeg')
        assert collection.generate_urls()


class ImageCollectionPropertyTestCase(BaseTestCase):
    def test_default_property_value(self):
        assert True
