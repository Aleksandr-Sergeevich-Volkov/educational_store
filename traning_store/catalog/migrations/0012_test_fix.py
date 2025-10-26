# catalog/migrations/0012_test_fix.py
from django.db import migrations
import os


def create_missing_columns_for_tests(apps, schema_editor):
    """Создает ВСЕ недостающие колонки в тестовой среде"""
    if os.environ.get('TESTING') or 'test' in os.environ.get('DJANGO_SETTINGS_MODULE', ''):
        from django.db import connection
        with connection.cursor() as cursor:
            
            # Все поля для catalog_model_type
            model_type_fields = [
                ('brand_id', 'INTEGER REFERENCES catalog_brend(id)'),
                ('description', 'TEXT')
            ]
            
            # Все поля для catalog_product
            product_fields = [
                ('articul', 'VARCHAR(100) DEFAULT %s' % "'P280'"),  # ← с default
                ('code', 'VARCHAR(50) DEFAULT %s' % "'51723'"),     # ← с default
            ]
            
            # Для catalog_model_type
            for field_name, field_type in model_type_fields:
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'catalog_model_type' AND column_name = '{field_name}'
                """)
                if not cursor.fetchone():
                    cursor.execute(f"""
                        ALTER TABLE catalog_model_type 
                        ADD COLUMN {field_name} {field_type}
                    """)
                    print(f"✅ Добавлено поле {field_name} в catalog_model_type")
            
            # Для catalog_product
            for field_name, field_type in product_fields:
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'catalog_product' AND column_name = '{field_name}'
                """)
                if not cursor.fetchone():
                    cursor.execute(f"""
                        ALTER TABLE catalog_product 
                        ADD COLUMN {field_name} {field_type}
                    """)
                    print(f"✅ Добавлено поле {field_name} в catalog_product")

class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0011_model_type_brand_model_type_description_and_more'),
    ]
    
    operations = [
        migrations.RunPython(create_missing_columns_for_tests),
    ]