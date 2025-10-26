# orders/migrations/0004_add_coupon_fields.py
from django.db import migrations, models
import django.db.models.deletion


def add_coupon_fields(apps, schema_editor):
    """Добавляет coupon_id и связанные поля в тестовой среде"""
    from django.db import connection
    with connection.cursor() as cursor:
        
        # Сначала создаем таблицу orders_coupon если нет
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'orders_coupon'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE orders_coupon (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(50) NOT NULL,
                    valid_from TIMESTAMP,
                    valid_to TIMESTAMP,
                    discount INTEGER NOT NULL,
                    active BOOLEAN NOT NULL
                )
            """)
            print("✅ Создана таблица orders_coupon")
        
        # Добавляем coupon_id если нет
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'orders_order' AND column_name = 'coupon_id'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE orders_order 
                ADD COLUMN coupon_id INTEGER REFERENCES orders_coupon(id)
            """)
            print("✅ Добавлено coupon_id в orders_order")
        
        # Добавляем discount если нет
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'orders_order' AND column_name = 'discount'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE orders_order 
                ADD COLUMN discount INTEGER DEFAULT 0
            """)
            print("✅ Добавлено discount в orders_order")
        
        # Добавляем delivery_sum если нет
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'orders_order' AND column_name = 'delivery_sum'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE orders_order 
                ADD COLUMN delivery_sum DECIMAL(10,2) DEFAULT 0
            """)
            print("✅ Добавлено delivery_sum в orders_order")


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0003_alter_order_address_pvz'),  # ← Зависит от последней миграции orders
    ]
    
    operations = [
        migrations.RunPython(add_coupon_fields),
    ]