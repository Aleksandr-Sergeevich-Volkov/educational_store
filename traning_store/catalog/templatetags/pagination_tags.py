from urllib.parse import urlencode

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    request = context['request']
    params = {}

    # Копируем текущие параметры
    for key, value in request.GET.items():
        if value and str(value).strip():
            params[key] = value

    # Обновляем переданными значениями
    for key, value in kwargs.items():
        if value:
            params[key] = value
        elif key in params:
            del params[key]

    # Возвращаем query string
    return urlencode(params) if params else ''
