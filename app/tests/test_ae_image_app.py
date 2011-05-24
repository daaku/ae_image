# -*- coding: utf-8 -*-
"""
Helpers for unit tests for ae_image.

"""
# pylint: disable=C0111

from ae_image_test import BaseTestCase


class AppTestCase(BaseTestCase):
    def test_home_page_renders_home(self):
        response = self.client.get('/')
        self.assert200(response)
        self.assertTemplateUsed('home.html')
