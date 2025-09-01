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
def cart_session():
    request = RequestFactory().get('/')
    middleware = SessionMiddleware(get_response=lambda r: None)
    middleware.process_request(request)
    return request.session.save()


class TestCart(TestCase):

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
    def test_add_cart(self, data):
        self.request = RequestFactory().get('/')
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(self.request)
        self.request.session.save()
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
def test_home_page(client):
    url = reverse('homepage:homepage')
    response = client.get(url)
    assert response.status_code, HTTPStatus.OK


@pytest.mark.django_db
def test_catalog(client):
    url = reverse('catalog:catalog')
    response = client.get(url)
    assert response.status_code, HTTPStatus.OK


@pytest.mark.django_db
def test_catalog_detail(data, client):
    product = get_object_or_404(Product, id=1)
    url = reverse('catalog:detail', kwargs={'slug': product.slug})
    response = client.get(url)
    assert response.status_code, HTTPStatus.OK
