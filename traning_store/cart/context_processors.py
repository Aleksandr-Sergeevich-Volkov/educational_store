# cart/context_processors.py
import logging
import os

import requests
from django.core.cache import cache
from dotenv import load_dotenv

from .cart import Cart

logger = logging.getLogger(__name__)

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


""" def weather(request):
    API_key = os.getenv('HEADERS')
    coordinates = {'Химки': [55.897, 37.4297], 'Хатанга': [71.964027, 102.440613]}
    lang = 'ru'
    celvin = 273.15
    city_temp = {}
    for city, coordinat in coordinates.items():
        lat, lon = coordinat
        ENDPOINT = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&lang={lang}'
        print(requests.get(ENDPOINT,))
        response = requests.get(ENDPOINT,)
        data = response.json().get('main')['temp']
        temp = round((data - celvin), 2)
        city_temp[city] = temp
    city_temp_str = ''
    for city_str, temp_str in city_temp.items():
        city_temp_str += f' {city_str}:{temp_str}'
    return {'city_temp': city_temp_str} """


def weather(request):
    """Context processor для погоды"""

    # Пытаемся взять из кэша
    cached_weather = cache.get('weather_cached')
    if cached_weather is not None:
        return {'city_temp': cached_weather}

    API_key = os.getenv('HEADERS')
    if not API_key:
        return {'city_temp': ''}

    coordinates = {'Химки': [55.897, 37.4297], 'Хатанга': [71.964027, 102.440613]}
    lang = 'ru'
    city_temp = {}

    for city, coordinat in coordinates.items():
        lat, lon = coordinat
        ENDPOINT = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&lang={lang}'

        for attempt in range(2):  # 2 попытки
            try:
                response = requests.get(ENDPOINT, timeout=5)

                if response.status_code == 200:
                    data = response.json().get('main')
                    if data and 'temp' in data:
                        celvin = 273.15
                        temp = round((data['temp'] - celvin), 1)
                        city_temp[city] = temp
                        break
                    else:
                        city_temp[city] = None
                        break  # Нет данных - не повторяем
                else:
                    logger.warning(f"Weather API status {response.status_code} for {city}")
                    city_temp[city] = None

            except requests.exceptions.Timeout:
                logger.warning(f"Weather timeout for {city}, attempt {attempt+1}")
                city_temp[city] = None
            except requests.exceptions.SSLError as e:
                logger.error(f"Weather SSL error for {city}: {e}")
                city_temp[city] = None
            except Exception as e:
                logger.error(f"Weather error for {city}: {e}")
                city_temp[city] = None

    # Формируем строку
    city_temp_str = ''
    for city_str, temp_str in city_temp.items():
        if temp_str is not None:
            city_temp_str += f' {city_str}:{temp_str}°'

    # Кэшируем на 30 минут при успехе
    if city_temp_str:
        cache.set('weather_cached', city_temp_str, 30 * 60)

    return {'city_temp': city_temp_str}
