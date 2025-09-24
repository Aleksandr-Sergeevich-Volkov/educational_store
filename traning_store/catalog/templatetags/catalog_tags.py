from catalog.models import Product
from django import template

register = template.Library()


@register.simple_tag()
def get_product(filter=None):
    if not filter:
        return Product.objects.all()
    else:
        return Product.objects.filter(brand__name=filter)
