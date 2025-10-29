from http import HTTPStatus

from cart.cart import Cart
from catalog.models import (Appointment, Brend, Color, Country, Gallery, Male,
                            Model_type, Product, Size)
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from orders.forms import OrderCreateForm
from orders.models import Order, OrderItem


class TestRoutes(TestCase):
    def setUp(self):
        # Создание базовых моделей
        self.country = Country.objects.create(name="Test Country")
        self.brend = Brend.objects.create(name="Test Brand", country_brand=self.country)
        self.appointment = Appointment.objects.create(name="Test Appointment")
        self.male = Male.objects.create(name="Test Male")

        # Создание цветов, размеров и типов моделей
        self.color = Color.objects.create(name="Черный")
        self.size = Size.objects.create(name="4", brand=self.brend)
        self.model_type = Model_type.objects.create(name="Стандартная", brand=self.brend)

        # Создание тестовых продуктов
        self.product1 = Product.objects.create(
            name="Test Product 1",
            slug="test-product-1",
            brend=self.brend,
            appointment=self.appointment,
            male=self.male,
            price=5999.00,
            available=True
        )
        self.product2 = Product.objects.create(
            name="Test Product 2",
            slug="test-product-2",
            brend=self.brend,
            appointment=self.appointment,
            male=self.male,
            price=6999.00,
            available=True
        )
        # Добавьте еще продукты если нужно для test_count_catalog
        self.product3 = Product.objects.create(
            name="Test Product 3",
            slug="test-product-3",
            brend=self.brend,
            appointment=self.appointment,
            male=self.male,
            price=7999.00,
            available=True
        )
        self.product4 = Product.objects.create(
            name="Test Product 4",
            slug="test-product-4",
            brend=self.brend,
            appointment=self.appointment,
            male=self.male,
            price=8999.00,
            available=True
        )

        # Создание галереи для продукта
        self.gallery1 = Gallery.objects.create(product=self.product1, image="test1.jpg")
        self.gallery2 = Gallery.objects.create(product=self.product1, image="test2.jpg")

        # Настройка запроса и корзины
        self.request = RequestFactory().get('/')
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(self.request)
        self.request.session.save()

    def test_count_catalog(self):
        catalog_count = Product.objects.count()
        self.assertEqual(catalog_count, 4)

    def test_add_cart(self):
        cart = Cart(self.request)
        images_m = Gallery.objects.filter(product=self.product1)

        cart.add(product=self.product1,
                 quantity=1,
                 size=self.size,
                 color=self.color,
                 m_type=self.model_type,
                 images_m=images_m)

        expected_cart_item = {
            'color': 'Черный',
            'images_m': str(images_m),  # Преобразуем QuerySet в строку для сравнения
            'm_type': 'Стандартная',
            'price': '5999.00',
            'quantity': 1,
            'size': '4'
        }

        self.assertEqual(cart.cart[str(self.product1.id)], expected_cart_item)

    def test_del_cart(self):
        cart = Cart(self.request)
        images_m = Gallery.objects.filter(product=self.product1)
        cart.add(product=self.product1,
                 quantity=1,
                 size=self.size,
                 color=self.color,
                 m_type=self.model_type,
                 images_m=images_m)
        cart.remove(self.product1)
        self.assertEqual(cart.cart, {})

    def test_create_order(self):
        initial_order_count = Order.objects.count()
        initial_order_item_count = OrderItem.objects.count()
        form = OrderCreateForm(data={
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'volkovaleksandrsergeevich@yandex.ru',
            'address': 'Адрес',
            'address_pvz': 'Адрес ПВЗ',
            'postal_code': 'Индекс',
            'city': 'Город'
        })

        self.assertTrue(form.is_valid())
        order = form.save()
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            price=5000,
            quantity=1
        )
        self.assertEqual(Order.objects.count(), initial_order_count + 1)
        self.assertEqual(OrderItem.objects.count(), initial_order_item_count + 1)

    def test_catalog_detail(self):
        url = reverse('catalog:detail', kwargs={'slug': self.product1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
