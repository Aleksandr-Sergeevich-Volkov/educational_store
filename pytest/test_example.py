from http import HTTPStatus

from django.core.management import call_command
from django.shortcuts import get_object_or_404
from django.urls import reverse

import pytest
from traning_store.catalog.models import Product


@pytest.fixture
def data():
    call_command('loaddata', 'db.json', verbosity=0)


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
