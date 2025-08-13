from http import HTTPStatus

import pytest
from django.urls import reverse


# Указываем в фикстурах встроенный клиент.
@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    # Адрес страницы получаем через reverse():
    url = reverse('homepage:homepage')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
