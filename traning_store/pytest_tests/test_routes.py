# news/tests/test_routes.py
import pprint
from http import HTTPStatus

from cart.cart import Cart
from catalog.models import Color, Gallery, Model_type, Product, Size
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from django.test import RequestFactory, TestCase
from django.urls import reverse
from orders.forms import OrderCreateForm
from orders.models import Order, OrderItem


class TestRoutes(TestCase):
    def setUp(self):
        call_command('loaddata', 'db.json', verbosity=0)
        self.request = RequestFactory().get('/')
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(self.request)
        self.request.session.save()

    def test_initialize_cart_clean_session(self):
        request = self.request
        cart = Cart(request)
        self.assertEqual(cart.cart, {})

    def test_home_page(self):
        url = reverse('homepage:homepage')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_catalog(self):
        url = reverse('catalog:catalog')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_count_catalog(self):
        catalog_count = Product.objects.count()
        self.assertEqual(catalog_count, 4)

    def test_add_cart(self):
        cart = Cart(self.request)
        product = get_object_or_404(Product, id=1)
        color = get_object_or_404(Color, id=1)
        size = get_object_or_404(Size, id=1)
        model_type = get_object_or_404(Model_type, id=1)
        images_m = Gallery.objects.filter(product=product)
        cart.add(product=product,
                 quantity=1,
                 size=size,
                 color=color,
                 m_type=model_type,
                 images_m=images_m,)
        pprint.pprint(vars(cart)['cart']['1'])
        test_cart = {'color': 'Черный',
                     'images_m': '<QuerySet [<Gallery: Gallery object (1)>, <Gallery: Gallery '
                     'object (2)>]>',
                     'm_type': 'Стандартная',
                     'price': '5999.00',
                     'quantity': 1,
                     'size': '4'}
        self.assertEqual(vars(cart)['cart']['1'], test_cart)

    def test_del_cart(self):
        cart = Cart(self.request)
        product = get_object_or_404(Product, id=1)
        color = get_object_or_404(Color, id=1)
        size = get_object_or_404(Size, id=1)
        model_type = get_object_or_404(Model_type, id=1)
        images_m = Gallery.objects.filter(product=product)
        cart.add(product=product,
                 quantity=1,
                 size=size,
                 color=color,
                 m_type=model_type,
                 images_m=images_m,)
        cart.remove(product)
        self.assertEqual(cart.cart, {})

    def test_create_order(self):
        form = OrderCreateForm(data={'first_name': 'Имя', 'last_name': 'Фамилия',
                                     'email': 'volkovaleksandrsergeevich@yandex.ru', 'address': 'Адрес',
                                     'address_pvz': 'Адрес ПВЗ', 'postal_code': 'Индекс',
                                     'city': 'Город'})
        order_count = Order.objects.count()
        order = form.save()
        order_item_count = OrderItem.objects.count()
        OrderItem.objects.create(order=order,
                                 product=get_object_or_404(Product, id=1),
                                 price=5000,
                                 quantity=1)
        self.assertEqual(Order.objects.count(), order_count + 1)
        self.assertEqual(OrderItem.objects.count(), order_item_count + 1)

    def test_catalog_detail(self):
        product = get_object_or_404(Product, id=1)
        url = reverse('catalog:catalog/' + product.slug)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
