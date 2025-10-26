# catalog/migrations/0013_fix_all_brand_columns.py
from django.db import migrations


def fix_all_brand_columns(apps, schema_editor):
    """Исправляет ВСЕ колонки brand на brand_id во ВСЕХ таблицах"""
    from django.db import connection
    with connection.cursor() as cursor:
        
        # Все таблицы где может быть колонка brand
        tables = ['catalog_size', 'catalog_model_type', 'catalog_product']
        
        for table in tables:
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}' AND column_name = 'brand'
            """)
            if cursor.fetchone():
                # Переименовываем brand в brand_id
                cursor.execute(f"ALTER TABLE {table} RENAME COLUMN brand TO brand_id")
                print(f"✅ Исправлено: brand -> brand_id в {table}")
                
            # Дополнительно создаем brand_id если его нет (для тестов)
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}' AND column_name = 'brand_id'
            """)
            if not cursor.fetchone():
                cursor.execute(f"""
                    ALTER TABLE {table} 
                    ADD COLUMN brand_id INTEGER REFERENCES catalog_brend(id)
                """)
                print(f"✅ Создано: brand_id в {table}")


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0012_test_fix'),
    ]
    
    operations = [
        migrations.RunPython(fix_all_brand_columns),
    ]