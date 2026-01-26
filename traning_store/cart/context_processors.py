import os

import requests
from dotenv import load_dotenv

from .cart import Cart

load_dotenv()


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


def weather(request):
    API_key = os.getenv('HEADERS')
    coordinates = {'Химки': [55.897, 37.4297], 'Колорадо-Спрингс': [38.8339, 104.821]}
    lang = 'ru'
    celvin = 273.15
    city_temp = {}
    for city, coordinat in coordinates.items():
        lat, lon = coordinat
        ENDPOINT = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&lang={lang}'
        response = requests.get(ENDPOINT,)
        data = response.json().get('main')['temp']
        temp = round((data - celvin), 2)
        city_temp[city] = temp
    city_temp_str = ''
    for city_str, temp_str in city_temp.items():
        city_temp_str += f' {city_str}:{temp_str}'
    return {'city_temp': city_temp_str}
