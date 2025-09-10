from http import HTTPStatus

import pytest
from cart.cart import Cart
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.management import call_command
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
