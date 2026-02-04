import logging
from decimal import Decimal

from catalog.models import Gallery, Product
from coupons.models import Coupon
from django.conf import settings

logger = logging.getLogger(__name__)


class Cart(object):

    def __init__(self, request):
        """
        Инициализируем корзину
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # сохранение текущего примененного купона
        self.coupon_id = self.session.get('coupon_id')
        self.cost = Decimal('5000.00')
        if self.session.get('delivery_cost'):
            self.delivery_cost = Decimal(self.session.get('delivery_cost'))

    def _generate_product_key(self, product, size, color, m_type):
        """Генерирует одинаковый ключ для add и remove"""
        product_id = str(product.id)

        # Обработка size
        if hasattr(size, 'name') and size.name:
            size_str = str(size.name)
        else:
            size_str = str(size)

        # Обработка color (теперь это объект Color)
        if color is None:
            raise ValueError("Пожалуйста, выберите цвет")

        if hasattr(color, 'name') and color.name:
            color_str = str(color.name)
        elif hasattr(color, 'id'):
            color_str = str(color.id)
        else:
            color_str = str(color)

        # Обработка m_type
        if hasattr(m_type, 'name') and m_type.name:
            m_type_str = str(m_type.name)
        else:
            m_type_str = str(m_type)

        return f"{product_id}_{size_str}_{color_str}_{m_type_str}"

    def get_product_quantity(self, product, size, color, m_type):
        """Получает текущее количество товара с конкретными характеристиками"""
        product_key = self._generate_product_key(product, size, color, m_type)
        if product_key in self.cart:
            return self.cart[product_key]['quantity']
        return 0

    def add(self, product, quantity=1, size='1', color='черный',
            m_type='Стандартный', images_m='1', update_quantity=False):
        # Добавить продукт в корзину или обновить его количество.
        # Создаем уникальный ключ на основе ID товара и его характеристик
        try:
            product_key = self._generate_product_key(product, size, color, m_type)
        except ValueError as e:
            # Возвращаем ошибку для отображения пользователю
            return str(e)
        if product_key not in self.cart:
            self.cart[product_key] = {
                'product_id': str(product.id),
                'quantity': 0,
                'price': str(product.price),
                'size': str(size.name) if size else str(product.Size.name),
                'color': str(color) if color else str(product.Color),
                'm_type': str(m_type.name) if m_type else str(product.Model_type.name),
                'images_m': str(Gallery.objects.filter(product=product))
            }
            print(f'add {self.cart[product_key]}')
        if update_quantity:
            self.cart[product_key]['quantity'] = quantity
        else:
            self.cart[product_key]['quantity'] += quantity
        self.save()

    def save(self):
        # Обновление сессии cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, product, size, color, m_type):
        """Удаляет товар с конкретными характеристиками из корзины"""
        product_key = self._generate_product_key(product, size, color, m_type)
        print(f'Key remove {product_key}')
        if product_key in self.cart:
            del self.cart[product_key]
            self.save()
        if self.session.get('delivery_cost') is not None:
            del self.session['delivery_cost']
            self.save()
        if self.session.get('delivery_address') is not None:
            del self.session['delivery_address']
            self.save()

    def __iter__(self):
        # Собираем настоящие ID товаров из сложных ключей
        product_ids = []

    # Извлекаем ID товаров из ключей (первая часть до первого '_')
        for key in self.cart.keys():
            product_id = key.split('_')[0]  # Берем только ID товара
            product_ids.append(product_id)

    # Получаем объекты продуктов
        products = Product.objects.filter(id__in=product_ids)

    # Создаем словарь для быстрого доступа к продуктам по ID
        product_dict = {str(product.id): product for product in products}

    # Обогащаем данные корзины информацией о продуктах
        for item_key, item in self.cart.items():
            # Получаем ID продукта из ключа
            product_id = item_key.split('_')[0]

            if product_id in product_dict:
                item['product'] = product_dict[product_id]
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                item['item_key'] = item_key  # Сохраняем ключ для использования в шаблонах
                yield item

    def __len__(self):
        # Подсчет всех товаров в корзине.
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        # Подсчет стоимости товаров в корзине.
        return sum(Decimal(item['price']) * item['quantity'] for item in
                   self.cart.values())

    def get_images(self, product):
        images_m = Gallery.objects.filter(product=product)
        return images_m[images_m]

    def clear(self):
        # удаление корзины из сессии
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
        if self.session.get('delivery_cost') is not None:
            del self.session['delivery_cost']
            self.session.modified = True
        if self.session.get('delivery_address') is not None:
            del self.session['delivery_address']
            self.session.modified = True

    @property
    def coupon(self):
        if self.coupon_id:
            return Coupon.objects.get(id=self.coupon_id)
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal('100')
                    ) * self.get_total_price()
        return Decimal('0')

    def delivery(self):
        if self.get_total_price() <= self.cost and self.__len__() != 0 and self.session.get('delivery_cost') is not None:
            return self.delivery_cost
        return Decimal('0')

    def get_total_price_after_discount(self):
        if self.delivery:
            return round((self.get_total_price() - self.get_discount()), 2) + self.delivery()
        return round((self.get_total_price() - self.get_discount()), 2)
