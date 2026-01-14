from django.core.management.base import BaseCommand
from homepage.models import City


class Command(BaseCommand):
    help = 'Заполняет базу основными городами России'

    def handle(self, *args, **options):
        cities = [
            ('Москва', 'Москва', True, True, 1),
            ('Санкт-Петербург', 'Санкт-Петербург', True, False, 2),
            ('Новосибирск', 'Новосибирская область', True, False, 3),
            ('Екатеринбург', 'Свердловская область', True, False, 4),
            ('Казань', 'Республика Татарстан', True, False, 5),
            ('Нижний Новгород', 'Нижегородская область', True, False, 6),
            ('Челябинск', 'Челябинская область', True, False, 7),
            ('Самара', 'Самарская область', True, False, 8),
            ('Омск', 'Омская область', True, False, 9),
            ('Ростов-на-Дону', 'Ростовская область', True, False, 10),
            ('Краснодар', 'Краснодарский край', False, False, 11),
            ('Воронеж', 'Воронежская область', False, False, 12),
        ]

        for name, region, is_popular, is_default, order in cities:
            City.objects.get_or_create(
                name=name,
                region=region,
                defaults={
                    'is_popular': is_popular,
                    'is_default': is_default,
                    'order': order,
                    'is_active': True,
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Добавлено {len(cities)} городов'))
