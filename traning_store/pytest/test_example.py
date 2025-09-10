from http import HTTPStatus

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.management import call_command
from django.test import RequestFactory
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
