# favorites/views.py
from catalog.models import Product
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .utils import SessionFavorites


def toggle_favorite(request, product_id):
    """Переключить избранное (с перезагрузкой)"""
    product = get_object_or_404(Product, id=product_id)
    session_fav = SessionFavorites(request)

    is_added = session_fav.toggle(product_id)

    if is_added:
        messages.success(request, f'✅ Товар "{product.name}" добавлен в избранное')
    else:
        messages.info(request, f'🗑️ Товар "{product.name}" удален из избранного')

    # Возврат на предыдущую страницу (как в корзине)
    return redirect(request.META.get("HTTP_REFERER", "catalog:catalog"))


def favorites_list(request):
    """Страница с избранными товарами"""
    session_fav = SessionFavorites(request)
    products = session_fav.get_products()

    return render(
        request,
        "list.html",
        {
            "products": products,
            "favorites_count": session_fav.count(),
        },
    )


def clear_favorites(request):
    """Очистить избранное"""
    if request.method == "POST":
        session_fav = SessionFavorites(request)
        session_fav.clear()
        messages.success(request, "🗑️ Избранное очищено")

    return redirect("favorites:favorites_list")
