"""
Сервисы для отправки сообщений в MAX API
"""
import json
import logging
from decimal import Decimal

import requests
from coupons.models import Coupon
from django.conf import settings

from .models import CartItem
from .state import get_cart_state, set_cart_state

logger = logging.getLogger(__name__)

MAX_API_URL = "https://platform-api.max.ru/messages"


def send_message(user_id, text, buttons=None):
    """Отправляет сообщение пользователю через MAX API"""

    headers = {
        "Authorization": settings.MAX_BOT_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {"text": text}

    if buttons:
        payload["attachments"] = [
            {
                "type": "inline_keyboard",
                "payload": {"buttons": buttons}
            }
        ]

    print(f"Payload_: {json.dumps(payload, ensure_ascii=False, indent=2)}")

    url = f"https://platform-api.max.ru/messages?user_id={user_id}"

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def send_message_with_image(user_id, text, image_url, buttons=None):
    """
    Отправляет сообщение с изображением и кнопками
    """
    headers = {
        "Authorization": settings.MAX_BOT_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {"text": text}

    # Собираем attachments
    attachments = []

    # Добавляем кнопки, если есть
    if buttons:
        attachments.append({
            "type": "inline_keyboard",
            "payload": buttons
        })

    # Добавляем изображение
    if image_url:
        attachments.append({
            "type": "image",
            "payload": {"url": image_url}
        })

    if attachments:
        payload["attachments"] = attachments
    print(f'payload_!_@_$_#: {payload}')

    url = f"https://platform-api.max.ru/messages?user_id={user_id}"

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


class CartService:
    """Сервис для работы с корзиной пользователя в боте"""

    def __init__(self, user_id):
        self.user_id = str(user_id)
        # Загружаем состояние корзины из Redis
        self.state = get_cart_state(self.user_id)
        self.coupon_id = self.state.get('coupon_id')

    def add(self, product, quantity=1, size=None, color=None, model_type=None):
        """
        Добавить товар в корзину.
        size, color, model_type — объекты моделей или None.
        """
        cart_item, created = CartItem.objects.get_or_create(
            user_id=self.user_id,
            product=product,
            size=size,
            color=color,
            model_type=model_type,
            defaults={
                'quantity': quantity,
                'price_at_add': product.price
            }
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    def remove(self, cart_item_id):
        """Удалить позицию из корзины по ID"""
        CartItem.objects.filter(id=cart_item_id, user_id=self.user_id).delete()
        self.set_coupon(None)

    def update_quantity(self, cart_item_id, quantity):
        """Изменить количество товара"""
        if quantity <= 0:
            self.remove(cart_item_id)
            return

        cart_item = CartItem.objects.filter(id=cart_item_id, user_id=self.user_id).first()
        if cart_item:
            cart_item.quantity = quantity
            cart_item.save()

    def get_items(self):
        """Получить все позиции корзины с предзагрузкой связанных данных"""
        return CartItem.objects.filter(
            user_id=self.user_id
        ).select_related(
            'product', 'size', 'color', 'model_type'
        )

    def save_state(self):
        """Сохраняет состояние корзины в Redis"""
        self.state['coupon_id'] = self.coupon_id
        set_cart_state(self.user_id, self.state)

    def set_coupon(self, coupon_id):
        """Устанавливает купон для корзины"""
        self.coupon_id = coupon_id
        self.save_state()

    @property
    def get_coupon(self):
        """Возвращает объект купона"""
        if self.coupon_id:
            print(self.coupon_id)
            try:
                return Coupon.objects.get(id=self.coupon_id, active=True)
            except Coupon.DoesNotExist:
                return None
        return None

    def get_total(self):
        # Подсчет стоимости товаров в корзине.
        return sum(item.get_total_price() for item in self.get_items())

    def get_discount(self):
        """Возвращает сумму скидки"""
        coupon = self.get_coupon
        if coupon:
            discount_percent = Decimal(str(coupon.discount))
            return (discount_percent / Decimal('100')) * self.get_total()
        return Decimal('0')

    def get_total_price(self):
        """Общая стоимость корзины"""
        total = Decimal('0')
        for item in self.get_items():
            total += item.get_total_price()
        print(f'self.get_discount():{self.get_discount()}')
        print(f'total: {total}')
        return total - self.get_discount()

    def get_total_items(self):
        """Общее количество товаров в корзине"""
        return sum(item.quantity for item in self.get_items())

    def clear(self):
        """Очистить корзину"""
        CartItem.objects.filter(user_id=self.user_id).delete()
        self.set_coupon(None)

    def is_empty(self):
        """Проверить, пуста ли корзина"""
        return not self.get_items().exists()
