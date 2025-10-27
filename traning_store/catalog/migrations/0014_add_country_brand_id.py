from django.db import migrations
import os


def add_country_brand_id(apps, schema_editor):
    """Добавляет country_brand_id в catalog_brend и устанавливает значение по умолчанию"""
    from django.db import connection
    with connection.cursor() as cursor:
        
        # Добавляем country_brand_id если нет
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'catalog_brend' AND column_name = 'country_brand_id'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE catalog_brend 
                ADD COLUMN country_brand_id INTEGER REFERENCES catalog_country(id)
            """)
            print("✅ Добавлено country_brand_id в catalog_brend")
        
        # Устанавливаем значение по умолчанию для существующих записей
        cursor.execute("""
            UPDATE catalog_brend 
            SET country_brand_id = 1 
            WHERE country_brand_id IS NULL
        """)
        print("✅ Установлены значения по умолчанию для country_brand_id")
        
        # Делаем поле NOT NULL
        cursor.execute("""
            ALTER TABLE catalog_brend 
            ALTER COLUMN country_brand_id SET NOT NULL
        """)
        print("✅ Установлен NOT NULL для country_brand_id")


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0013_fix_all_brand_columns'),  # ← Зависит от последней миграции catalog
    ]
    
    operations = [
        migrations.RunPython(add_country_brand_id),
    ]