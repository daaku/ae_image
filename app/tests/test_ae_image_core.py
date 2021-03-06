# -*- coding: utf-8 -*-
"""
Unit tests for ae_image.core.

"""
# pylint: disable=C0111

from ae_image_test import BaseTestCase
from google.appengine.ext.blobstore import BlobInfo
import ae_image.core


class StyleTestCase(BaseTestCase):
    def test_hash_equal_for_no_format_and_quality(self):
        style1 = ae_image.core.Style('style1')
        style2 = ae_image.core.Style('style2')
        self.assertEqual(hash(style1), hash(style2),
            'Hash for styles without format or quality must be the same.')

    def test_hash_equal_for_same_format(self):
        style1 = ae_image.core.Style('style1', format='jpeg')
        style2 = ae_image.core.Style('style2', format='jpeg')
        self.assertEqual(hash(style1), hash(style2),
            'Hash for styles with the same format and no quality must ' +
            'be the same.')

    def test_hash_equal_for_different_size(self):
        style1 = ae_image.core.Style('style1', size=42, format='jpeg')
        style2 = ae_image.core.Style('style2', size=420, format='jpeg')
        self.assertEqual(hash(style1), hash(style2),
            'Hash for styles with the same format and and different sizes ' +
            'must be the same.')

    def test_hash_equal_for_different_crop(self):
        style1 = ae_image.core.Style('style1', size=42, format='jpeg')
        style2 = ae_image.core.Style(
            'style2', size=42, crop=True, format='jpeg')
        self.assertEqual(hash(style1), hash(style2),
            'Hash for styles with the same format and and different crop ' +
            'setting must be the same.')

    def test_hash_not_equal_for_different_format(self):
        style1 = ae_image.core.Style('style1', format='jpeg')
        style2 = ae_image.core.Style('style2', format='gif')
        self.assertNotEqual(hash(style1), hash(style2),
            'Hash for styles with different formats must not be the same.')

    def test_hash_not_equal_for_different_quality(self):
        style1 = ae_image.core.Style('style1', format='jpeg', quality=70)
        style2 = ae_image.core.Style('style2', format='jpeg', quality=80)
        self.assertNotEqual(hash(style1), hash(style2),
            'Hash for styles with different quality must not be the same.')

    def test_crop_requires_size(self):
        self.assertRaises(ValueError, ae_image.core.Style, 'style1', crop=True)

    def test_quality_requires_jpeg(self):
        self.assertRaises(ValueError, ae_image.core.Style, 'style1',
            format='gif', quality=10)

    def test_repr_has_something(self):
        self.assertEqual(
            '<Style "style1" format=jpeg quality=10 size=10 (cropped)>',
            repr(ae_image.core.Style('style1', size=10, crop=True,
                    format='jpeg', quality=10)),
            'Expect repr back.')


class BlobTestCase(BaseTestCase):
    def test_repr_has_something(self):
        self.assertEqual(
            '<Blob "key": jpeg, Serving URL: url>',
            repr(ae_image.core.Blob('key', 'jpeg', 'url')),
            'Expect repr back.')


class ImageTestCase(BaseTestCase):
    def test_empty_image_has_no_url(self):
        image = ae_image.core.Image('abc', 'jpeg')
        self.assertEqual(len(image.blobs), 0,
            'Expect no blobs on a new image.')
        self.assertRaises(ae_image.core.UrlNotFound, image.get_url,
            ae_image.core.Style('original'))

    def test_image_with_original_url(self):
        image = ae_image.core.Image('abc', 'jpeg')
        image.generate_url(ae_image.core.Style('original'))
        self.assertEqual(len(image.blobs), 1,
            'Expect one blob on a new image.')
        self.assertTrue(
            image.get_url(ae_image.core.Style('original')),
            'Expect a URL for "original" style.')
        self.assertTrue(
            image.get_url(ae_image.core.Style('name_doesnt_matter')),
            'Expect a URL for original style independent of the name.')
        self.assertTrue(
            image.get_url(ae_image.core.Style('original', size=10)),
            'Expect a URL for original style independent of the size.')
        self.assertTrue(
            image.get_url(ae_image.core.Style('original', size=10, crop=True)),
            'Expect a URL for original style independent of the size or crop.')

    def test_image_with_existing_blobs(self):
        image1 = ae_image.core.Image('abc', 'jpeg')
        image1.generate_url(ae_image.core.Style('another', format='gif'))
        image1.generate_url(ae_image.core.Style('more', format='jpeg'))

        image2 = ae_image.core.Image('abc', 'jpeg', image1.blobs)
        self.assertEqual(len(image2.blobs), 2, 'Expect 2 blobs on image.')

    def test_generate_url_for_new_format(self):
        image = ae_image.core.Image('abc', 'jpeg')
        self.assertRaises(ae_image.core.UrlNotFound, image.get_url,
            ae_image.core.Style('another', format='gif'))
        image.generate_url(ae_image.core.Style('another', format='gif'))
        self.assertEqual(len(image.blobs), 1, 'Expect 1 blob on image.')
        self.assertTrue(
            image.get_url(ae_image.core.Style('another', format='gif')),
            'Expect a URL for newly generated style.')

    def test_raise_on_missing_url(self):
        image = ae_image.core.Image('abc', 'jpeg')
        try:
            image.get_url(
                ae_image.core.Style('another', format='gif'))
            self.fail('Was expecting a UrlNotFound exception.')
        except ae_image.core.UrlNotFound, ex:
            self.assertEqual(repr(ex),
                u'URL for blob_key "abc" for style "another" was not found.',
                'Expect formatted exception message.')

    def test_remove_image_with_only_original_blob(self):
        content_type = 'image/jpeg'
        blob_key = self.make_blob(content_type, 'dummy')
        self.assertTrue(BlobInfo.get(blob_key),
            'Should be able to load BlobInfo for key.')
        image = ae_image.core.Image(blob_key, content_type)
        image.remove()
        self.assertFalse(BlobInfo.get(blob_key),
            'Should no longer be able to load BlobInfo for key.')

    def test_remove_image_with_multiple_blobs(self):
        pass

    def test_repr_has_something(self):
        self.assertEqual(
            '<Image "key" with blobs {}>',
            repr(ae_image.core.Image('key', 'jpeg')),
            'Expect repr back.')


class CollectionTestCase(BaseTestCase):
    def test_empty_image_collection(self):
        collection = ae_image.core.Collection([])
        self.assertEqual(len(collection.images), 0, 'Expect no images.')

    def test_raise_on_unknown_style(self):
        blob_key = 'abc'
        collection = ae_image.core.Collection(
            [ae_image.core.Style('big', 500)])
        collection.append(blob_key, 'jpeg')
        try:
            collection.get_url('small', blob_key)
            self.fail('Was expecting UnknownStyle exception.')
        except ae_image.core.UnknownStyle, ex:
            self.assertEqual(repr(ex), u'Unknown style "small" requested.',
                'Expect formatted exception message.')

    def test_raise_on_unknown_image(self):
        collection = ae_image.core.Collection(
            [ae_image.core.Style('big', 500)])
        collection.append('abc', 'jpeg')
        try:
            collection.get_url('big', 'def')
            self.fail('Was expecting UnknownImage exception.')
        except ae_image.core.UnknownImage, ex:
            self.assertEqual(repr(ex),
                u'Unknown image blob_key "def" requested.',
                'Expect formatted exception message.')

    def test_get_valid_single_url(self):
        blob_key = 'abc'
        collection = ae_image.core.Collection(
            [ae_image.core.Style('big', 500)])
        collection.append(blob_key, 'jpeg')
        self.assertTrue(
            collection.get_url('big', blob_key), 'Expect URL back.')

    def test_append_from_blob_info(self):
        blob_key = self.make_blob('image/jpeg', 'dummy')
        collection = ae_image.core.Collection(
            [ae_image.core.Style('big', 500)])
        collection.append_from_blob_info(BlobInfo.get(blob_key))
        self.assertTrue(
            collection.get_url('big', blob_key), 'Expect URL back.')

    def test_get_valid_ordered_urls_for_all_images(self):
        blob_key0 = 'abc'
        blob_key1 = 'def'
        collection = ae_image.core.Collection(
            [ae_image.core.Style('big', 500)])
        collection.append(blob_key0, 'jpeg')
        collection.append(blob_key1, 'jpeg')
        urls = list(collection.get_urls('big'))
        self.assertEqual(len(urls), 2, 'Expect 2 URLs back.')
        self.assertEqual(urls[0][1], collection.get_url('big', blob_key0),
            'Expect URL for blob key 0.')
        self.assertEqual(urls[1][1], collection.get_url('big', blob_key1),
            'Expect URL for blob key 1.')

    def test_generate_urls_for_new_style(self):
        blob_key = 'abc'
        collection = ae_image.core.Collection(
            [ae_image.core.Style('big', 500)])
        collection.append(blob_key, 'jpeg')
        self.assertFalse(
            collection.generate_urls(), 'Expect nothing to generate.')
        collection.styles['low'] = ae_image.core.Style('low', format='jpeg')
        self.assertTrue(
            collection.generate_urls(), 'Expect to generate something.')

    def test_remove_with_single_image(self):
        blob_key = self.make_blob('image/jpeg', 'dummy')
        self.assertTrue(BlobInfo.get(blob_key),
            'Should be able to load BlobInfo for key.')
        collection = ae_image.core.Collection(
            [ae_image.core.Style('big', 500)])
        collection.append_from_blob_info(BlobInfo.get(blob_key))
        self.assertTrue(
            collection.get_url('big', blob_key), 'Expect URL back.')
        collection.remove(blob_key)
        self.assertFalse(BlobInfo.get(blob_key),
            'Should no longer be able to load BlobInfo for key.')
        self.assertRaises(ae_image.core.UnknownImage, collection.get_url,
            'big', blob_key)
        self.assertRaises(ae_image.core.UnknownImage, collection.remove,
            blob_key)

    def test_repr_has_something(self):
        expected = '''Collection:
styles: {'original': <Style "original">, 'another': <Style "another">}
images: OrderedDict()'''
        self.assertEqual(expected,
            repr(ae_image.core.Collection([ae_image.core.Style('another')])),
            'Expect repr back.')
