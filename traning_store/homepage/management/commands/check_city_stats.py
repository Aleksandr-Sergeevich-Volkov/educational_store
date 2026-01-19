# management/commands/check_city_stats.py
from django.core.management.base import BaseCommand
from homepage.models import City


class Command(BaseCommand):
    help = 'Проверяет статистику определений городов'

    def handle(self, *args, **options):
        from django.db.models import Sum

        total = City.objects.aggregate(total=Sum('detection_count'))['total'] or 0

        self.stdout.write("=" * 60)
        self.stdout.write("СТАТИСТИКА ОПРЕДЕЛЕНИЙ ГОРОДОВ:")
        self.stdout.write("=" * 60)

        cities = City.objects.filter(detection_count__gt=0).order_by('-detection_count')

        for city in cities:
            percentage = (city.detection_count / total * 100) if total > 0 else 0
            self.stdout.write(
                f"{city.name:20} {city.region:30} "
                f"{city.detection_count:8} раз "
                f"({percentage:6.2f}%)"
            )

        self.stdout.write("=" * 60)
        self.stdout.write(f"Всего определений: {total}")
        self.stdout.write(f"Городов с определениями: {cities.count()}")
