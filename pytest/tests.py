from http import HTTPStatus

from django.urls import reverse


def test_home_page(client):
    url = reverse('homepage:homepage')
    response = client.get(url)
    assert response.status_code, HTTPStatus.OK
