import logging

from django import forms

from .models import Order

logger = logging.getLogger(__name__)


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'address_pvz',
                  'postal_code', 'city']
