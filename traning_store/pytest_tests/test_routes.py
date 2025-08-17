# news/tests/test_routes.py
from http import HTTPStatus

from catalog.models import Product
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse


class TestRoutes(TestCase):
    def setUp(self):
        # Load fixtures
        call_command('loaddata', 'db.json', verbosity=0)

    def test_home_page(self):
        url = reverse('homepage:homepage')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_catalog(self):
        url = reverse('catalog:catalog')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_count_catalog(self):
        catalog_count = Product.objects.count()
        self.assertEqual(catalog_count, 4)
