from datetime import datetime

from catalog.models import Product, Type_product
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Только каталоги с 2+ изображениями
        catalogs = []
        for cat in Type_product.objects.filter(
            name__in=['Компрессионные чулки', 'Компрессионные гольфы', 'Компрессионные колготки']
        ):
            images = list(cat.type_images.all()[:2])
            if len(images) == 2:
                catalogs.append({
                    'id': f'cat_{cat.id}',
                    'url': f'https://kompressionnye-chulki24.ru/search/?query={cat.name.split()[-1]}',
                    'pictures': [f'https://kompressionnye-chulki24.ru{img.image.url}' for img in images],
                    'name': f'{cat.name} - Интернет магазин-компрессионные_чулки24',
                    'description': cat.description or f'Купить {cat.name.lower()}',
                })

        # Товары
        cat_ids = [c['id'].replace('cat_', '') for c in catalogs]
        products = Product.objects.filter(
            available=True,
            Type_product_id__in=cat_ids
        ).select_related('Type_product')

        # Маппинг категорий
        cat_map = {
            'Компрессионные чулки': 10,
            'Компрессионные гольфы': 20,
            'Компрессионные колготки': 30
        }

        # Данные товаров
        products_data = []
        for p in products:
            img = p.images.filter(main=True).first() or p.images.first()
            products_data.append({
                'id': p.id,
                'name': p.name,
                'price': p.price,
                'slug': p.slug,
                'main_image_url': img.image.url if img else '',
                'category_id': cat_map.get(p.Type_product.name, 1),
                'collection_id': f'cat_{p.Type_product.id}',
            })

        # Генерация XML
        xml_content = render_to_string('yml_feed.xml', {
            'current_date': datetime.now().strftime("%Y-%m-%dT%H:%M+03:00"),
            'products': products_data,
            'collections': catalogs,
        })

        # Сохранение файла
        file_path = '/var/www/html/goods_chulki.xml'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        self.stdout.write(
            self.style.SUCCESS(f'✅ YML feed generated: {file_path} ({len(catalogs)} cats, {len(products_data)} offers)')
        )
