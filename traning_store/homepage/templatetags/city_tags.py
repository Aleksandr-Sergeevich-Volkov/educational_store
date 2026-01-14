from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_current_city(context):
    """Возвращает текущий город из контекста"""
    return context.get('current_city')


@register.inclusion_tag('includes/city_selector.html', takes_context=True)
def city_selector(context):
    """Шаблонный тег для выбора города"""
    return {
        'current_city': context.get('current_city'),
        'popular_cities': context.get('popular_cities', []),
        'request': context.get('request'),
    }
