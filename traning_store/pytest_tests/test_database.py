from django.test import TestCase
from django.db import connection

class TestDatabaseStructure(TestCase):
    def test_database_columns(self):
        """Проверяем структуру тестовой БД"""
        with connection.cursor() as cursor:
            # Проверим catalog_size в тестовой БД
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'catalog_size'")
            columns = [row[0] for row in cursor.fetchall()]
            print("Тестовая БД - колонки catalog_size:", columns)
            
            self.assertIn('brand_id', columns, "В тестовой БД нет колонки brand_id!")