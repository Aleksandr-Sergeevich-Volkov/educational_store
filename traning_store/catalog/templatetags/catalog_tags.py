from urllib.parse import urlencode

from catalog.models import Product
from django import template

register = template.Library()


# Ваш существующий тег
@register.simple_tag()
def get_product(filter=None):
    if not filter:
        return Product.objects.all()
    else:
        return Product.objects.filter(brand__name=filter)


# НОВЫЙ тег для удаления параметров
@register.simple_tag
def remove_query_param(request, param_to_remove):
    """
    Удаляет параметр из текущего URL.

    Пример: <a href="{% remove_query_param request 'brand' %}">Удалить бренд</a>
    """
    params = {}

    # Копируем все параметры кроме удаляемого
    for key, value in request.GET.items():
        if key != param_to_remove and value and str(value).strip():
            params[key] = value

    # Возвращаем query string
    if params:
        return '?' + urlencode(params)
    return '?'


# Альтернативный простой тег
@register.simple_tag
def get_url_without_param(request, param_name):
    """
    Простая версия без context.

    Пример: <a href="{% get_url_without_param request 'brand' %}">
    """
    params = {}

    for key, value in request.GET.items():
        if key != param_name and value and str(value).strip():
            params[key] = value

    if params:
        return '?' + urlencode(params)
    return '?'
