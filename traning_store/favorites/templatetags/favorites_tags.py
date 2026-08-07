# favorites/templatetags/favorites_tags.py
from django import template
from favorites.utils import SessionFavorites

register = template.Library()


@register.simple_tag(takes_context=True)
def is_favorite(context, product):
    """Проверка, находится ли товар в избранном"""
    request = context["request"]
    session_fav = SessionFavorites(request)
    return session_fav.is_favorite(product.id)


@register.inclusion_tag("button.html", takes_context=True)
def favorite_button(context, product, size="md", show_text=True):
    """Кнопка избранного (без JS)"""
    request = context["request"]
    session_fav = SessionFavorites(request)

    return {
        "product": product,
        "is_favorite": session_fav.is_favorite(product.id),
        "size": size,
        "show_text": show_text,
    }
