"""проверка стоимости доставки."""
import logging
import os
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv

load_dotenv()
PRACTICUM_TOKEN = os.getenv('P_TOKEN')
TELEGRAM_TOKEN = os.getenv('T_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_PERIOD = 600
VIEWING_PERIOD = 2592000
ENDPOINT = 'https://b2b.taxi.tst.yandex.net/api/b2b/platform/pricing-calculator'
HEADERS = {'Authorization': os.getenv('HEADERS')}

""" def check_tokens():
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    chat_id = TELEGRAM_CHAT_ID
    logging.info('Проверка отправки сообщения')
    try:
        bot.send_message(chat_id, message)
    except telegram.error.TelegramError as telegram_error:
        logging.error(f'Сбой отпраки сообщения {telegram_error}')
    except Exception as error:
        logging.error(error)
    else:
        logging.debug('Успешная отправка сообщения') """


def get_api_answer(timestamp):
    timestamp = timestamp or int(time.time())
    payload = {'from_date': timestamp}
    logging.info('Проверка отправки запроса')
    try:
        data = {'destination': {'platform_station_id': 'fbed3aa1-2cc6-4370-ab4d-59c5cc9bb924'}, 'source': {'platform_station_id': '03840f16-3c53-400c-b382-1ecf30e06b64'},
                'tariff': 'self_pickup', 'total_weight': 1000, 'client_price': 0, 'payment_method': 'already_paid', 'places': [
               {"physical_dims": {"weight_gross": 5000, "dx": 50, "dy": 50, "dz": 50, "predefined_volume": 1000}}], 'total_assessed_price': 500}
        homework_statuses = requests.post(
            ENDPOINT,
            headers=HEADERS,
            json=data,
        )
    except requests.RequestException as error:
        raise Exception(f'Ошибка запроса {error}, {HEADERS}, {payload}')
    else:
        logging.info('Успешная отправка запроса')
    if homework_statuses.status_code != HTTPStatus.OK:
        # raise Exception('Ошибка код ответа не равен 200')
        print(homework_statuses.status_code)
    logging.info('Проверка получения ответа')
    return homework_statuses.json()


print(get_api_answer(int(time.time())))
