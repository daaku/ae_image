# -*- coding: utf-8 -*-
"""
Core Python type which is made available as the property value. This
exposes the structured public interface for the serialized data stored in the
underlying property. You will use the ``ImageProperty`` to define
your model and the property value on model instances will be an instance of
the ``Collection`` class defined here.

"""

from google.appengine.api.images import get_serving_url
from ordereddict import OrderedDict
from os import environ
import google.appengine.ext.blobstore as blobstore

_is_dev_environment = environ.get('SERVER_SOFTWARE', '').startswith('Dev')


class UrlNotFound(Exception):
    """
    If a serving URL is requested for a style that has not been stored, this
    exception will be raised.

    """

    def __init__(self, blob_key, style_name):
        super(UrlNotFound, self).__init__()
        self.blob_key = str(blob_key)
        self.style_name = style_name

    def __repr__(self):
        data = {
            u'blob_key': self.blob_key,
            u'name': self.style_name,
        }
        return (u'URL for blob_key "%(blob_key)s" ' +
                u'for style "%(name)s" was not found.') % data


class UnknownStyle(Exception):
    """
    If a requested named style is not found, this exception will be raised.

    """

    def __init__(self, style_name):
        super(UnknownStyle, self).__init__()
        self.style_name = style_name

    def __repr__(self):
        return u'Unknown style "%s" requested.' % self.style_name


class UnknownImage(Exception):
    """
    If a requested image identified by it's blob_key is not found, this
    exception will be raised.

    """

    def __init__(self, blob_key):
        super(UnknownImage, self).__init__()
        self.blob_key = blob_key

    def __repr__(self):
        return u'Unknown image blob_key "%s" requested.' % self.blob_key


class Style(object):
    """
    Defines a "style" an image is available in.

    """

    def __init__(self, name, size=None, crop=None, format=None, quality=None):
        self.name = name
        self.size = size

        if crop and not size:
            raise ValueError('"cropy" requires "size" to be specified.')
        self.crop = crop

        if quality and not format:
            format = 'jpeg'
        self.format = format

        if quality and format != 'jpeg':
            raise ValueError(
                '"quality" can only be specified with format=jpeg')
        self.quality = quality

    def __repr__(self):
        ret = u'<Style "%s"' % self.name
        if self.format:
            ret += u' format=%s' % self.format
        if self.quality:
            ret += u' quality=%d' % self.quality
        if self.size:
            ret += u' size=%d' % self.size
        if self.crop:
            ret += u' (cropped)'
        ret += '>'
        return ret

    def serving_key(self):
        """
        We only use the format and quality as the rest of the parameters do not
        affect the base serving URL, and are applied on top of it.

        """

        return (self.format, self.quality)

    def __eq__(self, other):
        return self.serving_key() == other.serving_key()

    def __hash__(self):
        return hash(self.serving_key())


class Blob(object):
    """
    Defines a blob storing an image and associated serving URL.

    """

    def __init__(self, blob_key, content_type, serving_url):
        self.blob_key = str(blob_key)
        self.content_type = content_type
        self.serving_url = serving_url

    def __repr__(self):
        return u'<Blob "%s": %s, Serving URL: %s>' % \
            (self.blob_key, self.content_type, self.serving_url)


class Image(object):
    """
    Represents an original image and various styles of that image.

    """

    def __init__(self, blob_key, content_type, blobs=None):
        self.blob_key = str(blob_key)
        self.content_type = content_type
        self.blobs = blobs or {}
        #TODO automatically do lossless conversions like bmp/tiff to png

    def __repr__(self):
        return '<Image "%s" with blobs %r>' % (self.blob_key, self.blobs)

    def get_url(self, style):
        """Get a URL for this image based on the given style."""

        try:
            url = self.blobs[style].serving_url
            if style.size:
                url += '=s%d' % style.size
            if style.crop:
                url += '-c'
            return url
        except KeyError, _ex:
            raise UrlNotFound(self.blob_key, style.name)

    def generate_url(self, style):
        """
        Generate a URL for the image based on the given style. Returns ``True``
        if a new URL was generated and the instance was modified.

        """

        if style not in self.blobs:
            #TODO handle format conversion
            serving_url = get_serving_url(self.blob_key)

            # in the development environment it is not desirable to have the
            # address/port in the serving url
            if _is_dev_environment:
                serving_url = serving_url[serving_url.find('/', 9):]

            self.blobs[style] = \
                Blob(self.blob_key, self.content_type, serving_url)
            return True
        return False

    def remove(self):
        """
        Remove the original image blob and any additional blobs we may have
        created.

        """

        blobstore.delete(
            [self.blob_key] + [b.blob_key for b in self.blobs.values()])


class Collection(object):
    """
    The "image collection" is the core abstraction your application interacts
    with. You define a set of "styles" the images in this collection will be
    utilized in, add/remove images as well as get serving URLs for the
    named styles.

    """

    def __init__(self, styles, images=None):
        self.styles = dict([(s.name, s) for s in styles])
        if 'originl' not in self.styles:
            self.styles['original'] = Style('original')
        self.images = images or OrderedDict()

    def __repr__(self):
        return 'Collection:\nstyles: %r\nimages: %r' % \
            (self.styles, self.images)

    def get_url(self, style_name, blob_key):
        """Get the serving URL for the given blob_key in the named style."""

        blob_key = str(blob_key)

        try:
            style = self.styles[style_name]
        except KeyError, _ex:
            raise UnknownStyle(style_name)

        try:
            image = self.images[blob_key]
        except KeyError, _ex:
            raise UnknownImage(blob_key)

        return image.get_url(style)

    def get_urls(self, style_name):
        """
        Iterator to get serving URLs for all images in this collection for the
        named style.

        """

        for image in self.images.values():
            yield image.blob_key, image.get_url(self.styles[style_name])

    def generate_urls(self):
        """
        This will generate URLs for all defined styles. It will return
        ``True`` if a new URL was generated and the data needs to get saved.

        """

        modified = False
        for image in self.images.values():
            for style in self.styles.values():
                if image.generate_url(style):
                    modified = True
        return modified

    def append(self, blob_key, content_type):
        """
        Add a new image identified by the given blob_key and generate the
        necessary URLs for the configured styles.

        """

        blob_key = str(blob_key)
        self.images[blob_key] = image = Image(blob_key, content_type)
        map(image.generate_url, self.styles.values())
        return self

    def append_from_blob_info(self, blob_info):
        """Add a new image from the given blob_info object."""

        return self.append(blob_info.key(), blob_info.content_type)

    def remove(self, blob_key):
        """
        Remove the image identified by the given blob_key and associated data.

        """

        blob_key = str(blob_key)

        try:
            image = self.images.pop(blob_key)
        except KeyError, _ex:
            raise UnknownImage(blob_key)

        image.remove()
        return self
