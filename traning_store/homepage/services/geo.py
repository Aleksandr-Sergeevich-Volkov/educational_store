import logging

logger = logging.getLogger(__name__)


class SimpleGeolocation:

    @staticmethod
    def get_client_ip(request):
        """
        Получает IP с учетом nginx заголовков
        """
        # Проверяем заголовки от nginx
        ip_sources = [
            'HTTP_X_REAL_IP',        # nginx: proxy_set_header X-Real-IP
            'HTTP_X_FORWARDED_FOR',  # Цепочка прокси
            'REMOTE_ADDR',           # Прямое соединение
        ]

        for source in ip_sources:
            ip = request.META.get(source)
            if ip:
                # Если X-Forwarded-For содержит несколько IP
                if source == 'HTTP_X_FORWARDED_FOR' and ',' in ip:
                    ip = ip.split(',')[0].strip()

                # Очищаем IP
                ip = ip.strip()
                print(f"DEBUG: Found IP from {source}: {ip}")

                # Возвращаем первый найденный валидный IP
                if ip and ip != 'unknown':
                    return ip

        return '127.0.0.1'

    @staticmethod
    def get_city_by_ip(ip):
        """
        Определяет город по IP
        Для разработки с Docker используем тестовые данные
        """
        # Тестовые данные для разработки
        test_cities = [
            ('Москва', 'Москва'),
            ('Санкт-Петербург', 'Санкт-Петербург'),
            ('Новосибирск', 'Новосибирская область'),
            ('Екатеринбург', 'Свердловская область'),
            ('Казань', 'Республика Татарстан'),
            ('Нижний Новгород', 'Нижегородская область'),
            ('Челябинск', 'Челябинская область'),
            ('Самара', 'Самарская область'),
            ('Омск', 'Омская область'),
            ('Ростов-на-Дону', 'Ростовская область'),
        ]

        # Если IP локальный (Docker сеть), используем тестовые данные
        if ip.startswith('172.') or ip in ['127.0.0.1', 'localhost']:
            # Детерминированный выбор на основе IP
            try:
                last_octet = int(ip.split('.')[-1])
                city_index = last_octet % len(test_cities)
                return test_cities[city_index]
            except ValueError:
                # Ошибка преобразования в int (например, если не число)
                # Пример: ip = "172.18.abc.1"
                logger.warning(f"ValueError: Cannot parse IP '{ip}', last octet is not a number")
                return test_cities[0]  # Москва по умолчанию:

        # Для реальных IP используем API (позже)
        # Пока возвращаем тестовые
        return test_cities[0]
