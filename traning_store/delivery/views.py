import logging
import os

import requests
from django.shortcuts import render
from dotenv import load_dotenv

from .forms import DeliveryForm

load_dotenv()
logger = logging.getLogger(__name__)


def delivery_add(request):
    ENDPOINT = 'https://b2b-authproxy.taxi.yandex.net/api/b2b/platform/pricing-calculator'
    logger.warning(f'test {os.getenv('HEADERS_Delivery')}')
    HEADERS = {'Authorization': os.getenv('HEADERS_Delivery')}
    form = DeliveryForm(request.GET or None)
    if form.is_valid():
        pvz_id = form.cleaned_data['pvz_id']
        data = {'destination': {'platform_station_id': pvz_id}, 'source': {'platform_station_id': '01978d0f333b73d680d32e7d696090e3'},
                'tariff': 'self_pickup', 'total_weight': 500, 'client_price': 0, 'payment_method': 'already_paid', 'places': [
               {"physical_dims": {"weight_gross": 500, "dx": 40, "dy": 25, "dz": 7, "predefined_volume": 7000}}], 'total_assessed_price': 500}
        homework_statuses = requests.post(
            ENDPOINT,
            headers=HEADERS,
            json=data,
        )
        cost_ = homework_statuses.json().get('pricing_total')
        request.session['delivery_cost'] = homework_statuses.json().get('pricing_total').replace('RUB', "")
        request.session['delivery_address'] = form.cleaned_data['address_pvz']
        return render(request, 'deliverys.html', {'cost': cost_})
    else:
        form = DeliveryForm()
    return render(request, 'delivery.html', {'form': form, })
