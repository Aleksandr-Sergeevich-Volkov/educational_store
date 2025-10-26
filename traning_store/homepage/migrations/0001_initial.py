# homepage/migrations/0001_initial.py
from django.db import migrations
import os


def create_homepage_tables(apps, schema_editor):
    """Создает таблицы homepage если их нет"""
    if os.environ.get('TESTING') or 'test' in os.environ.get('DJANGO_SETTINGS_MODULE', ''):
        from django.db import connection
        with connection.cursor() as cursor:
            
            # Создаем таблицу homepage_post если нет
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'homepage_post'
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE homepage_post (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(256) NOT NULL,
                        text TEXT NOT NULL
                    )
                """)
                print("✅ Создана таблица homepage_post")
            
            # Создаем таблицу homepage_comment если нет
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'homepage_comment'
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE homepage_comment (
                        id SERIAL PRIMARY KEY,
                        text TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        post_id INTEGER REFERENCES homepage_post(id),
                        author_id INTEGER REFERENCES auth_user(id)
                    )
                """)
                print("✅ Создана таблица homepage_comment")


class Migration(migrations.Migration):
    initial = True  # ← Это первая миграция

    dependencies = [
        # Пусто - это первая миграция
    ]
    
    operations = [
        migrations.RunPython(create_homepage_tables),
    ]