import requests

from .cart import Cart


def cart(request):
    return {'cart': Cart(request)}


def user_context_processor(request):
    return {
        'is_authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else 'войдите или зарегистрируйтесь',
    }


def currency(request):
    ENDPOINT = 'https://www.cbr-xml-daily.ru/latest.js'
    response = requests.get(ENDPOINT,)
    data = response.json().get('rates')
    EUR = round(1 / data['EUR'], 2)
    TRY = round(1 / data['TRY'], 2)
    USD = round(1 / data['USD'], 2)
    return {'EUR': f'EUR: {EUR}',
            'TRY': f'TRY: {TRY}',
            'USD': f'USD: {USD}'}
