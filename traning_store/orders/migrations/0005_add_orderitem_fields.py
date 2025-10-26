# orders/migrations/0005_add_orderitem_fields.py
from django.db import migrations, models
import django.db.models.deletion

def add_orderitem_fields(apps, schema_editor):
    """Добавляет недостающие поля в orders_orderitem"""
    from django.db import connection
    with connection.cursor() as cursor:
        
        # Добавляем size_id если нет
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'orders_orderitem' AND column_name = 'size_id'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE orders_orderitem 
                ADD COLUMN size_id INTEGER REFERENCES catalog_size(id) DEFAULT 4
            """)
            print("✅ Добавлено size_id в orders_orderitem")
        
        # Добавляем color_id если нет
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'orders_orderitem' AND column_name = 'color_id'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE orders_orderitem 
                ADD COLUMN color_id INTEGER REFERENCES catalog_color(id) DEFAULT 1
            """)
            print("✅ Добавлено color_id в orders_orderitem")
        
        # Добавляем m_type_id если нет
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'orders_orderitem' AND column_name = 'm_type_id'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE orders_orderitem 
                ADD COLUMN m_type_id INTEGER REFERENCES catalog_model_type(id) DEFAULT 1
            """)
            print("✅ Добавлено m_type_id в orders_orderitem")

class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0004_add_coupon_fields'),  # ← Зависит от предыдущей миграции orders
    ]
    
    operations = [
        migrations.RunPython(add_orderitem_fields),
    ]