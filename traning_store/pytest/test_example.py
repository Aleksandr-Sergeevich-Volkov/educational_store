import pytest
from django.core.management import call_command


@pytest.fixture
def data():
    call_command('loaddata', 'db.json', verbosity=0)
