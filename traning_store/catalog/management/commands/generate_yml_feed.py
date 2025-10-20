# catalog/management/commands/generate_yml_feed.py
import os
from datetime import datetime

from catalog.models import Product
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = 'Generate YML feed XML file for nginx'

    def handle(self, *args, **options):
        products = Product.objects.filter(available=True).select_related(
            'brand', 'Type_product', 'Class_compress'
        ).prefetch_related('images')

        current_date = datetime.now().strftime("%Y-%m-%dT%H:%M+03:00")

        context = {
            'current_date': current_date,
            'products': products,
        }

        # Генерируем XML
        xml_content = render_to_string('yml_feed.xml', context)

        # Сохраняем в файл для nginx
        file_path = os.path.join(settings.BASE_DIR, 'static', 'goods_chulki.xml')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated YML feed: {file_path}')
        )
