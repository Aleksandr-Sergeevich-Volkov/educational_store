# news/tests/test_routes.py
import pprint
from http import HTTPStatus

from cart.cart import Cart
from catalog.models import Color, Gallery, Model_type, Product, Size
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from django.test import RequestFactory, TestCase
from django.urls import reverse


class TestRoutes(TestCase):
    def setUp(self):
        call_command('loaddata', 'db.json', verbosity=0)
        self.request = RequestFactory().get('/')
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(self.request)
        self.request.session.save()

    def test_initialize_cart_clean_session(self):
        request = self.request
        cart = Cart(request)
        self.assertEqual(cart.cart, {})

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

    def test_add_cart(self):
        cart = Cart(self.request)
        product = get_object_or_404(Product, id=1)
        color = get_object_or_404(Color, id=1)
        size = get_object_or_404(Size, id=1)
        model_type = get_object_or_404(Model_type, id=1)
        images_m = Gallery.objects.filter(product=product)
        cart.add(product=product,
                 quantity=1,
                 size=size,
                 color=color,
                 m_type=model_type,
                 images_m=images_m,)
        pprint.pprint(vars(cart))
        self.assertEqual(len(cart), 1)
