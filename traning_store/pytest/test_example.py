from http import HTTPStatus

import pytest
from cart.cart import Cart
from catalog.models import Product
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from django.test import RequestFactory
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


@pytest.mark.django_db
def test_initialize_cart_clean_session(client):
    request = RequestFactory().get('/')
    middleware = SessionMiddleware(get_response=lambda r: None)
    middleware.process_request(request)
    request.session.save()
    request = client.request
    cart = Cart(request)
    assert cart.cart == {}


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
