# catalog/migrations/0012_test_fix.py
from django.db import migrations
import os


def create_missing_columns_for_tests(apps, schema_editor):
    """Создает недостающие колонки только в тестовой среде"""
    if os.environ.get('TESTING') or 'test' in os.environ.get('DJANGO_SETTINGS_MODULE', ''):
        from django.db import connection
        with connection.cursor() as cursor:
            # Только в тестах создаем недостающие колонки
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'catalog_size' AND column_name = 'brand_id'
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    ALTER TABLE catalog_size 
                    ADD COLUMN brand_id INTEGER REFERENCES catalog_brend(id)
                """)
            
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'catalog_model_type' AND column_name = 'brand_id'
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    ALTER TABLE catalog_model_type 
                    ADD COLUMN brand_id INTEGER REFERENCES catalog_brend(id)
                """)


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0009_gallery_main'),
    ]
    
    operations = [
        migrations.RunPython(create_missing_columns_for_tests),
    ]