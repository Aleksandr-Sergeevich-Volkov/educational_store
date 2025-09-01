from http import HTTPStatus

import pytest
from catalog.models import Product
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from django.urls import reverse


@pytest.fixture
def data():
    call_command('loaddata', 'db.json', verbosity=0)


# @pytest.fixture(scope='session')
# def django_db_setup(django_db_setup, django_db_blocker):
#    with django_db_blocker.unblock():
#        call_command('loaddata', 'db.json')


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
