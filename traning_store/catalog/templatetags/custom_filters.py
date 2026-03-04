from django import template

register = template.Library()


@register.filter
def extract_middle(value):
    """Извлекает текст между дефисом и вертикальной чертой"""
    if not value:
        return value
    if '-' in value and '|' in value:
        # Берем все после дефиса до черты
        after_dash = value.split('-', 1)[-1]
        return after_dash.split('|', 1)[0].strip()
    elif '|' in value:
        return value.split('|', 1)[0].strip()
    return value.strip()
