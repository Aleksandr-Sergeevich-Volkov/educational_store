from http import HTTPStatus

import pytest
from cart.cart import Cart
from catalog.models import Color, Gallery, Model_type, Product, Size
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from django.test import RequestFactory, TestCase
from django.urls import reverse


@pytest.fixture
def data():
    call_command('loaddata', 'db.json', verbosity=0)


@pytest.fixture
def cart_session_():
    request = RequestFactory().get('/')
    middleware = SessionMiddleware(get_response=lambda r: None)
    middleware.process_request(request)
    return request.session.save()


@pytest.mark.django_db
def test_home_page(client):
    url = reverse('homepage:homepage')
    response = client.get(url)
    assert response.status_code, HTTPStatus.OK


class TestCart(TestCase):
    @pytest.fixture
    @pytest.mark.django_db
    def cart_session(self):
        self.request = RequestFactory().get('/')
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(self.request)
        self.request.session.save()

    @pytest.mark.django_db
    def test_initialize_cart_clean_session(self):
        self.request = RequestFactory().get('/')
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(self.request)
        self.request.session.save()
        request = self.request
        cart = Cart(request)
        assert cart.cart == {}

    @pytest.mark.django_db
    @pytest.mark.usefixtures('data', 'cart_session')
    def test_add_cart(self):
        request = self.request
        cart = Cart(request)
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
        test_cart = {'color': 'Черный',
                     'images_m': '<QuerySet [<Gallery: Gallery object (1)>, <Gallery: Gallery '
                     'object (2)>]>',
                     'm_type': 'Стандартная',
                     'price': '5999.00',
                     'quantity': 1,
                     'size': '4'}
        assert vars(cart)['cart']['1'] == test_cart


@pytest.mark.django_db
def test_count_catalog(data):
    print(Product.objects.all())
    catalog_count = Product.objects.count()
    assert catalog_count == 4
