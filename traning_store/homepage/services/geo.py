import logging

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)


class SimpleGeolocation:
    """
    Простой сервис для определения города по IP
    Использует бесплатные публичные API
    """

    @staticmethod
    def get_city_by_ip(ip):
        """
        Определяет город и регион по IP адресу
        Возвращает (city, region) или (None, None)
        """
        # Проверяем кэш (24 часа)
        cache_key = f'geo_ip_{ip}'
        cached = cache.get(cache_key)
        if cached:
            return cached.get('city'), cached.get('region')

        # Локальные IP
        if ip in ['127.0.0.1', 'localhost', '::1', '0.0.0.0']:
            return 'Москва', 'Москва'

        # Пробуем разные API (бесплатные)

        # 1. ip-api.com (150 запросов/мин, без регистрации)
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}?lang=ru', timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    city = data.get('city', '')
                    region = data.get('regionName', '')
                    if city and region:
                        result = {'city': city, 'region': region}
                        cache.set(cache_key, result, 86400)  # 24 часа
                        return city, region

        except requests.exceptions.RequestException as e:
            logger.debug(f"ip-api.com failed for {ip}: {e}")
        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"ip-api.com JSON parsing error for {ip}: {e}")

        # 2. ipapi.co (1000 запросов/день, без регистрации)
        try:
            response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=2)
            if response.status_code == 200:
                data = response.json()
                city = data.get('city', '')
                region = data.get('region', '')
                if city and region:
                    result = {'city': city, 'region': region}
                    cache.set(cache_key, result, 86400)
                    return city, region

        except requests.exceptions.RequestException as e:
            logger.debug(f"ipapi.co failed for {ip}: {e}")
        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"ipapi.co JSON parsing error for {ip}: {e}")

        # 3. get.geojs.io (бесплатно, без лимитов но менее точный)
        try:
            response = requests.get(f'https://get.geojs.io/v1/ip/geo/{ip}.json', timeout=2)
            if response.status_code == 200:
                data = response.json()
                city = data.get('city', '')
                region = data.get('region', '')
                if city and region:
                    result = {'city': city, 'region': region}
                    cache.set(cache_key, result, 86400)
                    return city, region

        except requests.exceptions.RequestException as e:
            logger.debug(f"get.geojs.io failed for {ip}: {e}")
        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"get.geojs.io JSON parsing error for {ip}: {e}")

        return None, None

    @staticmethod
    def get_client_ip(request):
        """
        Получает реальный IP адрес клиента из запроса
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            # Берем первый IP из списка
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

        return ip
