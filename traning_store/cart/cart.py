import logging
# import pprint
from decimal import Decimal

from catalog.models import Gallery, Product
from coupons.models import Coupon
from django.conf import settings

# from django.contrib.sessions.backends.db import SessionStore

logger = logging.getLogger(__name__)


class Cart(object):

    def __init__(self, request):
        """
        Инициализируем корзину
        """
        # request.session = SessionStore()
        self.session = request.session
        print(self.session.get(settings.CART_SESSION_ID))
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

    def add(self, product, quantity=1, size='1', color='черный',
            m_type='Стандартный', images_m='1', update_quantity=False):
        # Добавить продукт в корзину или обновить его количество.
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price),
                                     'size': str(product.Size),
                                     'color': str(product.Color),
                                     'm_type': str(product.Model_type),
                                     'images_m': str(Gallery.objects.filter(
                                                     product=product))
                                     }
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # Обновление сессии cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, product):
        # Удаление товара из корзины.
        product_id = str(product.id)
        if product_id in self.cart :
            del self.cart[product_id]
            self.save()
        if self.session.get('delivery_cost') is not None:
            del self.session['delivery_cost']
            self.save()

    def __iter__(self):
        # Перебор элементов в корзине и получение продуктов из базы данных.
        product_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product
        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
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
