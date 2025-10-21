from datetime import datetime

from catalog.models import Gallery, Product
from django.core.management.base import BaseCommand
from django.db.models import Prefetch
from django.template.loader import render_to_string


class Command(BaseCommand):
    def handle(self, *args, **options):
        main_images_prefetch = Prefetch(
            'images',
            queryset=Gallery.objects.filter(main=True),
            to_attr='main_images'
        )

        products = Product.objects.filter(available=True).select_related(
            'brand', 'Type_product', 'Class_compress'
        ).prefetch_related(main_images_prefetch)

        products_data = []
        for product in products:
            main_image = product.main_images[0] if product.main_images else product.images.first()

            category_id = self.get_category_id(product)

            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'slug': product.slug,
                'main_image_url': main_image.image.url if main_image else '',
                'category_id': category_id,
                'type_product_name': product.Type_product.name if product.Type_product else '',
            })

        current_date = datetime.now().strftime("%Y-%m-%dT%H:%M+03:00")

        context = {
            'current_date': current_date,
            'products': products_data,
        }

        # Используем просто 'yml_feed.xml' для общей папки templates
        xml_content = render_to_string('yml_feed.xml', context)

        file_path = '/var/www/html/goods_chulki.xml'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated YML feed: {file_path}')
        )

    def get_category_id(self, product):
        """Определяет ID категории на основе типа продукта"""
        if not product.Type_product:
            return 1

        type_mapping = {
            'Компрессионные чулки': 10,
            'Компрессионные гольфы': 20,
            'Компрессионные колготки': 30,
        }

        return type_mapping.get(product.Type_product.name, 1)
