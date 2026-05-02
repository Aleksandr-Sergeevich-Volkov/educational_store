# max_bot/favorites_service.py
from catalog.models import Product

from .models import FavoriteItem


def add_to_favorites(user_id, product_id):
    """
    Добавляет товар в избранное для пользователя MAX.
    Возвращает True, если товар был добавлен, и False, если уже был в избранном.
    """
    try:
        product = Product.objects.get(id=product_id, available=True)
        _, created = FavoriteItem.objects.get_or_create(
            user_id=str(user_id),
            product=product
        )
        return created
    except Product.DoesNotExist:
        return False


def remove_from_favorites(user_id, product_id):
    """Удаляет товар из избранного"""
    deleted, _ = FavoriteItem.objects.filter(
        user_id=str(user_id),
        product_id=product_id
    ).delete()
    return deleted > 0


def get_favorites(user_id):
    """Возвращает QuerySet избранных товаров пользователя"""
    return FavoriteItem.objects.filter(
        user_id=str(user_id)
    ).select_related('product')


def is_favorite(user_id, product_id):
    """Проверяет, находится ли товар в избранном у пользователя"""
    return FavoriteItem.objects.filter(
        user_id=str(user_id),
        product_id=product_id
    ).exists()
