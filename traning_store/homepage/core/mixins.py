import logging

import requests
from django.core.cache import cache
from django.db import DatabaseError, models

from ..models import City

logger = logging.getLogger(__name__)


class CityContextMixin:
    """
    Миксин для добавления города в контекст всех View.
    Обрабатывает определение города через сессию, IP и выбор пользователя.
    """

    # Можно переопределить в наследниках
    default_city_name = "Москва"
    popular_cities_limit = 10
    cache_timeout = 86400  # 24 часа

    def get_city_context(self, request):
        """Возвращает словарь с контекстом города для шаблона"""
        city = self.get_current_city(request)

        return {
            'current_city': city,
            'popular_cities': self.get_popular_cities(),
            'city_stats': self.get_city_stats(),  # Добавляем статистику
            'nearby_cities': self.get_nearby_cities(city) if city else [],
            'all_cities': self.get_all_cities() if request.user.is_staff else [],
        }

    def get_current_city(self, request):
        """
        Основной метод определения текущего города:
        1. Проверяем сессию
        2. Проверяем GET параметр (если пользователь сменил город)
        3. Определяем по IP
        4. Берем город по умолчанию
        """
        # 1. Проверяем GET параметр (пользователь выбрал город)
        city_id_from_get = request.GET.get('city_id')
        if city_id_from_get:
            city = self.get_city_by_id(city_id_from_get)
            if city:
                request.session['current_city_id'] = city.id
                # УВЕЛИЧИВАЕМ СЧЕТЧИК ПРИ РУЧНОЙ СМЕНЕ ГОРОДА
                self.increment_city_detection_count(city)
                return city

        # 2. Проверяем сессию
        city_id = request.session.get('current_city_id')
        if city_id:
            city = self.get_city_by_id(city_id)
            if city:
                return city

        # 3. Определяем по IP
        city = self.detect_city_by_ip(request)
        if city:
            request.session['current_city_id'] = city.id
            return city

        # 4. Город по умолчанию
        default_city = self.get_default_city()
        if default_city:
            request.session['current_city_id'] = default_city.id
            # УВЕЛИЧИВАЕМ СЧЕТЧИК ДЛЯ ГОРОДА ПО УМОЛЧАНИЮ
            self.increment_city_detection_count(default_city)
        return default_city

    def get_city_by_id(self, city_id, increment_count=True):
        """Безопасное получение города по ID"""
        try:
            city = City.objects.get(id=city_id, is_active=True)
            # Опционально увеличиваем счетчик
            if increment_count:
                self.increment_city_detection_count(city)
            return city
        except (City.DoesNotExist, ValueError):
            return None

    def detect_city_by_ip(self, request):
        """
        Определяет город по IP адресу пользователя
        Использует внешние сервисы с кэшированием
        """
        ip = self.get_client_ip(request)

        # Пропускаем локальные IP
        if ip in ['127.0.0.1', 'localhost', '::1']:
            return self.get_default_city()

        # Проверяем кэш
        cache_key = f'city_by_ip_{ip}'
        cached_city_id = cache.get(cache_key)

        if cached_city_id:
            return self.get_city_by_id(cached_city_id)

        # Определяем город через внешний сервис
        city_data = self.get_city_from_ip_service(ip)
        if not city_data:
            return None

        # Ищем город в нашей базе
        city = self.find_city_in_database(
            city_data.get('city'),
            city_data.get('region')
        )

        if city:
            # Кэшируем результат
            cache.set(cache_key, city.id, self.cache_timeout)

            # Увеличиваем счетчик определений
            self.increment_city_detection_count(city)

        return city

    def get_client_ip(self, request):
        """Получает реальный IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Берем первый IP из списка
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip

    def get_city_from_ip_service(self, ip):
        """
        Определяет город по IP через внешний сервис
        Можно добавить резервные сервисы
        """
        try:
            # Используем ip-api.com (бесплатно, до 150 запросов/мин)
            response = requests.get(
                f'http://ip-api.com/json/{ip}?lang=ru',
                timeout=2
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'city': data.get('city'),
                        'region': data.get('regionName'),
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'lat': data.get('lat'),
                        'lon': data.get('lon'),
                    }
        except requests.RequestException:
            pass

        return None

    def find_city_in_database(self, city_name, region_name):
        """
        Ищет город в базе данных по названию и региону
        """
        if not city_name:
            return None

        # Сначала ищем точное совпадение по городу и региону
        if city_name and region_name:
            city = City.objects.filter(
                name__iexact=city_name,
                region__icontains=region_name,
                is_active=True
            ).first()
            if city:
                return city

        # Ищем только по названию города
        if city_name:
            city = City.objects.filter(
                name__iexact=city_name,
                is_active=True
            ).first()
            if city:
                return city

        # Ищем по частичному совпадению названия
        if city_name:
            city = City.objects.filter(
                name__icontains=city_name,
                is_active=True
            ).first()
            return city

        return None

    def increment_city_detection_count(self, city):
        """Увеличивает счетчик определений города"""
        try:
            from django.db import transaction
            from django.db.models import F

            with transaction.atomic():
                # Используем update для атомарности
                City.objects.filter(id=city.id).update(
                    detection_count=F('detection_count') + 1
                )
                # Обновляем объект в памяти
                city.refresh_from_db(fields=['detection_count'])
                logger.info(f"Incremented detection count for {city.name}: {city.detection_count}")

        except DatabaseError as e:
            logger.error(f"Database error incrementing detection count for city {city.id}: {e}")

        except Exception as e:
            logger.error(f"Error incrementing detection count for city {city.id}: {e}")

    def get_default_city(self):
        """Получает город по умолчанию"""
        # Сначала ищем город, помеченный как default
        city = City.objects.filter(is_default=True, is_active=True).first()
        if city:
            return city

        # Затем самый популярный
        city = City.objects.filter(is_popular=True, is_active=True).first()
        if city:
            return city

        # Затем просто первый активный
        return City.objects.filter(is_active=True).first()

    def get_popular_cities(self, limit=None):
        """Получает список популярных городов"""
        if limit is None:
            limit = self.popular_cities_limit

        # Сначала сортируем по счетчику определений, затем по флагу популярности
        return City.objects.filter(
            is_active=True
        ).order_by('-detection_count', '-is_popular', 'order')[:limit]

    def get_nearby_cities(self, current_city):
        """
        Получает города рядом с текущим (опционально)
        Можно реализовать логику на основе координат
        """
        if hasattr(current_city, 'latitude') and current_city.latitude:
            # Пример: города из того же региона
            return City.objects.filter(
                region=current_city.region,
                is_active=True
            ).exclude(id=current_city.id)[:5]
        return []

    def get_all_cities(self):
        """Получает все города (только для админов)"""
        if hasattr(self, 'show_all_cities') and self.show_all_cities:
            return City.objects.filter(is_active=True).order_by('name')
        return []

    def update_city_in_session(self, request, city_id):
        """
        Обновляет город в сессии
        Вызывается из других методов при смене города
        """
        if city_id:
            request.session['current_city_id'] = city_id
            request.session.modified = True
            return True
        return False

    def get_city_stats(self):
        """Получает статистику по городам"""
        from django.db.models import Sum

        stats = City.objects.aggregate(
            total_detections=Sum('detection_count'),
            total_cities=models.Count('id'),
            active_cities=models.Count('id', filter=models.Q(is_active=True)),
        )

        return {
            'total_detections': stats['total_detections'] or 0,
            'total_cities': stats['total_cities'],
            'active_cities': stats['active_cities'],
            'top_cities': City.objects.filter(
                detection_count__gt=0
            ).order_by('-detection_count')[:5],
        }
