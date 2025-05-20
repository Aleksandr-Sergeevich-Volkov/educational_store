import logging

from django import forms
from django.db import models

from .models import Order

logger = logging.getLogger(__name__)


class OrderCreateForm(forms.ModelForm):
    first_name = models.CharField('Имя', max_length=20)
    last_name = models.CharField('Фамилия', max_length=20)
    email = models.EmailField('Почта', max_length=300)
    address = models.CharField('Адрес', max_length=20)
    address_pvz = models.CharField('Адрес ПВЗ', max_length=20)
    postal_code = models.CharField('Индекс', max_length=20)
    city = models.CharField('Город', max_length=20)

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'address_pvz',
                  'postal_code', 'city']
        labels = {'first_name': 'Имя', 'last_name': 'Фамилия',
                  'email': 'Почта', 'address': 'Адрес',
                  'address_pvz': 'Адрес ПВЗ', 'postal_code': 'Индекс',
                  'city': 'Город'}
