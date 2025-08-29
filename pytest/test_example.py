from http import HTTPStatus

from django.urls import reverse

import pytest


@pytest.mark.django_db
def test_home_page(client):
    url = reverse('homepage:homepage')
    response = client.get(url)
    assert response.status_code, HTTPStatus.OK
