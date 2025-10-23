import pytest
from django.core.management import call_command


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Принудительно применяем миграции перед всеми тестами"""
    with django_db_blocker.unblock():
        call_command('migrate', verbosity=0)
        print("✅ Миграции применены для тестовой БД")


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Включаем доступ к БД для всех тестов"""
    pass


@pytest.fixture(autouse=True)
def create_test_data(db):
    """Создаем тестовые данные для всех тестов"""
    from catalog.models import Brend, Size, Model_type
    # Создаем данные только если их нет
    if not Brend.objects.exists():
        brand = Brend.objects.create(name="Test Brand")
        Size.objects.create(name="1", brand=brand)
        Size.objects.create(name="2", brand=brand)
        Model_type.objects.create(name="Test Model", brand=brand, description="Test")
        print("✅ Тестовые данные созданы")
