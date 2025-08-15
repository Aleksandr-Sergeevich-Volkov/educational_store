# news/tests/test_routes.py
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class TestRoutes(TestCase):

    def test_home_page(self):
        url = reverse('homepage:homepage')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_catalog(self):
        url = reverse('catalog:catalog')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
    
