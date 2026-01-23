import logging
import os
from typing import Optional, Tuple

import requests
from django.core.cache import cache
from django.db import transaction
from dotenv import load_dotenv
from models import City

logger = logging.getLogger(__name__)

load_dotenv()


class SimpleGeolocation:

    @staticmethod
    def get_client_ip(request):
        """
        Извлекает реальный IP из цепочки X-Forwarded-For
        Формат: "реальный_ip, nginx_ip, gateway_ip"
        """
        # 1. Проверяем X-Forwarded-For (самый надежный)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if x_forwarded_for:
            # Разбиваем цепочку: "87.255.16.119, 172.18.0.1"
            ips = [ip.strip() for ip in x_forwarded_for.split(',')]

            # Ищем первый не-Docker, не-localhost IP
            for ip in ips:
                if ip and SimpleGeolocation._is_external_ip(ip):
                    print(f"✅ Found real IP from X-Forwarded-For: {ip}")
                    return ip

        # 2. Проверяем X-Real-IP (может быть Docker IP)
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip and SimpleGeolocation._is_external_ip(x_real_ip):
            print(f"✅ Found real IP from X-Real-IP: {x_real_ip}")
            return x_real_ip

        # 3. Для разработки или если нет внешнего IP
        print('⚠️ No external IP found, using emulation')
        return SimpleGeolocation._emulate_ip(request)

    @staticmethod
    def _is_external_ip(ip):
        """Проверяет, является ли IP внешним (не внутренним)"""
        if not ip or ip.lower() == 'unknown':
            return False

        # Список внутренних IP
        internal_ranges = [
            '127.', '10.', '172.16.', '172.17.', '172.18.',
            '172.19.', '172.20.', '172.21.', '172.22.', '172.23.',
            '172.24.', '172.25.', '172.26.', '172.27.', '172.28.',
            '172.29.', '172.30.', '172.31.', '192.168.',
            '::1', 'localhost', '0.0.0.0'
        ]

        return not any(ip.startswith(prefix) for prefix in internal_ranges)

    @staticmethod
    def _emulate_ip(request):
        """Эмуляция IP для разработки (когда нет реального)"""
        # Используем сессию для постоянства
        import hashlib

        session_key = request.session.session_key or 'no_session'
        session_hash = hashlib.md5(session_key.encode()).hexdigest()
        hash_int = int(session_hash, 16)

        test_ips = [
            '95.84.217.66',    # Москва
            '78.155.196.194',  # Санкт-Петербург
            '188.233.237.38',  # Новосибирск
        ]

        index = hash_int % len(test_ips)
        return test_ips[index]

    @staticmethod
    def get_city_by_ip(ip):
        """
        Определяет город по реальному IP
        Использует API для реальных IP, тестовые для внутренних
        """
        # Если IP внутренний - используем тестовые данные
        if not SimpleGeolocation._is_external_ip(ip):
            return SimpleGeolocation._get_test_city_for_ip(ip)

        # Для реальных IP используем API
        print(f"🌍 Looking up real IP {ip} via API...")
        return SimpleGeolocation._get_real_city_by_ip(ip)

    @staticmethod
    def _get_test_city_for_ip(ip):
        """Тестовые города для внутренних IP"""
        test_cities = [
            ('Москва', 'Москва'),
            ('Санкт-Петербург', 'Санкт-Петербург'),
            ('Новосибирск', 'Новосибирская область'),
        ]

        try:
            # Детерминированный выбор на основе IP
            last_octet = int(ip.split('.')[-1])
            return test_cities[last_octet % len(test_cities)]
        except ValueError:
            # Ошибка преобразования в int (например, если не число)
            # Пример: ip = "172.18.abc.1"
            logger.warning(f"ValueError: Cannot parse IP '{ip}', last octet is not a number")
            return test_cities[0]  # Москва по умолчанию:

    @staticmethod
    def _get_real_city_by_ip(ip) -> Tuple[str, str]:
        """Получение реального города через ipinfo.io"""
        # Проверяем кэш
        cache_key = f'geo_real_{ip}'
        cached = cache.get(cache_key)
        if cached:
            print(f"📦 From cache: {cached}")
            return cached.get('city'), cached.get('region')

        try:
            # Получаем токен
            token = os.getenv('IPINFO_TOKEN')
            url = f'https://ipinfo.io/{ip}/json'
            params = {'token': token} if token else {}

            response = requests.get(url, params=params, timeout=3)
            data = response.json()

            # Получаем данные (латиница)
            city_lat = data.get('city', '').strip()
            region_lat = data.get('region', '').strip()
            country_code = data.get('country', '')

            if city_lat and region_lat and country_code == 'RU':
                # ✅ СОХРАНЯЕМ ГОРОД В БАЗУ (без передачи IP)
                SimpleGeolocation._save_city_simple(city_lat, region_lat)

                # Кэшируем
                result = {'city': city_lat, 'region': region_lat}
                cache.set(cache_key, result, 3600)
                print(f"✅ City from API: {city_lat}, {region_lat}")

                return city_lat, region_lat
            else:
                print(f"⚠️ No Russian city found for IP {ip}")
                return SimpleGeolocation._get_fallback_city(ip)

        except Exception as e:
            print(f"❌ API error: {e}")
            return SimpleGeolocation._get_fallback_city(ip)

    @staticmethod
    def _save_city_simple(city_lat: str, region_lat: str) -> Optional['City']:
        """
        ПРОСТОЙ способ: сохраняем город как есть
        city_lat - название города на латинице (Moscow)
        region_lat - название региона на латинице (Moscow Oblast)
        """
        if not City:
            return None

        try:
            with transaction.atomic():
                # Ищем город по латинскому названию
                city_obj = City.objects.filter(
                    name=city_lat,
                    region=region_lat
                ).first()

                if city_obj:
                    # Город уже есть - увеличиваем счетчик
                    city_obj.detection_count += 1
                    city_obj.save(update_fields=['detection_count', 'updated_at'])
                    print(f"   🔄 City exists: {city_lat} (count: {city_obj.detection_count})")
                else:
                    # Создаем новый город
                    city_obj = City.objects.create(
                        name=city_lat,           # Латинское название
                        name_ru=city_lat,        # Пока тоже латиница (админ поправит)
                        region=region_lat,       # Латинское название региона
                        country='Russia',
                        detection_count=1,
                        is_active=True,
                    )
                    print(f"   ✅ NEW CITY ADDED: {city_lat}, {region_lat}")

                return city_obj

        except Exception as e:
            print(f"   ❌ Error saving city: {e}")
            return None
