import os

import django
from catalog.models import Product
from django.db import transaction

# Настройка Django для скрипта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()


def generate_seo_for_empty_fields():
    """
    Безопасная генерация SEO только для пустых полей.
    Запуск: docker-compose exec web python generate_seo.py
    """
    print("🚀 Запуск безопасной генерации SEO полей...")
    print("=" * 60)

    # Фильтруем товары с пустыми SEO полями
    products = Product.objects.filter(
        seo_title=''
    ) | Product.objects.filter(
        seo_description=''
    ) | Product.objects.filter(
        seo_keywords=''
    ) | Product.objects.filter(
        seo_alt=''
    )

    total = products.distinct().count()

    if total == 0:
        print("✅ Все SEO поля уже заполнены! Ничего обновлять не нужно.")
        return

    print(f"📊 Найдено {total} товаров с пустыми SEO полями")
    print("=" * 60)

    stats = {
        'title': 0,
        'description': 0,
        'keywords': 0,
        'alt': 0,
        'h1': 0,
    }

    with transaction.atomic():
        for i, product in enumerate(products.distinct(), 1):
            updated = False

            # 1. SEO Title
            if not product.seo_title or product.seo_title.strip() == '':
                old_title = product.seo_title
                product.seo_title = ''  # очищаем для генерации
                product.save()
                if old_title != product.seo_title:
                    stats['title'] += 1
                    updated = True

            # 2. SEO Description
            if not product.seo_description or product.seo_description.strip() == '':
                old_desc = product.seo_description
                product.seo_description = ''
                product.save()
                if old_desc != product.seo_description:
                    stats['description'] += 1
                    updated = True

            # 3. SEO Keywords
            if not product.seo_keywords or product.seo_keywords.strip() == '':
                old_keywords = product.seo_keywords
                product.seo_keywords = ''
                product.save()
                if old_keywords != product.seo_keywords:
                    stats['keywords'] += 1
                    updated = True

            # 4. SEO Alt
            if not product.seo_alt or product.seo_alt.strip() == '':
                old_alt = product.seo_alt
                product.seo_alt = ''
                product.save()
                if old_alt != product.seo_alt:
                    stats['alt'] += 1
                    updated = True

            # 5. SEO H1 (если нужно)
            if not product.seo_h1 or product.seo_h1.strip() == '':
                product.seo_h1 = product.name[:255]
                product.save()
                stats['h1'] += 1
                updated = True

            # Прогресс
            if updated:
                print(f"✅ [{i:3d}/{total:3d}] Обновлен: {product.name[:40]}...")

            if i % 10 == 0:
                print(f"📊 Обработано {i}/{total} ({i/total*100:.1f}%)")

    print("=" * 60)
    print("🎉 ГЕНЕРАЦИЯ SEO ЗАВЕРШЕНА!")
    print("📈 Статистика обновлений:")
    print(f"   ├─ SEO Title:       {stats['title']:3d}")
    print(f"   ├─ SEO Description: {stats['description']:3d}")
    print(f"   ├─ SEO Keywords:    {stats['keywords']:3d}")
    print(f"   ├─ SEO Alt:         {stats['alt']:3d}")
    print(f"   └─ SEO H1:          {stats['h1']:3d}")
    print("=" * 60)


if __name__ == "__main__":
    generate_seo_for_empty_fields()
