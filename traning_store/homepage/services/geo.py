import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)


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
    def _get_real_city_by_ip(ip):
        """Получение реального города через API"""
        # Проверяем кэш
        cache_key = f'geo_real_{ip}'
        cached = cache.get(cache_key)
        if cached:
            print(f"📦 From cache: {cached}")
            return cached.get('city'), cached.get('region')

        # Пробуем API
        apis = [
            {
                'name': 'ip-api',
                'url': f'http://ip-api.com/json/{ip}?lang=ru',
                'parser': lambda d: (d.get('city'), d.get('regionName'))
                if d.get('status') == 'success' else (None, None)
            },
            {
                'name': 'ipapi',
                'url': f'https://ipapi.co/{ip}/json/',
                'parser': lambda d: (d.get('city'), d.get('region'))
            },
        ]

        for api in apis:
            try:
                import requests
                response = requests.get(api['url'], timeout=2)
                response.raise_for_status()
                data = response.json()

                city, region = api['parser'](data)

                if city and region:
                    result = {'city': city, 'region': region}
                    cache.set(cache_key, result, 3600)  # Кэш на 1 час
                    print(f"✅ API {api['name']} found: {city}, {region}")
                    return city, region

            except Exception as e:
                print(f"❌ API {api['name']} failed: {e}")
                continue

        # Если API не сработали, используем fallback
        print('⚠️ All APIs failed, using fallback')
        return SimpleGeolocation._get_fallback_city(ip)
