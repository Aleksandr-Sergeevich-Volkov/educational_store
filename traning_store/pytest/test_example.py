from http import HTTPStatus

import pytest
from cart.cart import Cart
from catalog.models import (Appointment, Brend, Class_compress, Color, Country,
                            Gallery, Male, Model_type, Product, Size, Soсk,
                            Type_product)
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.urls import reverse
from orders.forms import OrderCreateForm
from orders.models import Order, OrderItem


@pytest.fixture
def test_data(db):
    """Создает полные тестовые данные для всех тестов"""
    # Создание базовых моделей
    country = Country.objects.create(name="Test Country")
    brend = Brend.objects.create(name="Test Brand", country_brand=country)
    appointment = Appointment.objects.create(name="Test Appointment")
    male = Male.objects.create(name="Test Male")
    class_compress = Class_compress.objects.create(name="2 class")
    color_black = Color.objects.create(name="black", color='000000')
    color_white = Color.objects.create(name="white", color='FFFFFF')
    color_red = Color.objects.create(name="red", color='FF0000')
    sock = Soсk.objects.create(name="Closed")
    type_product = Type_product.objects.create(name="Chulki")

    # Создание размеров и типов моделей
    size = Size.objects.create(name="4", brand=brend)
    model_type = Model_type.objects.create(name="Стандартная", brand=brend)

    # Создание тестовых продуктов
    product1 = Product.objects.create(
        name="Test Product 1",
        slug="test-product-1",
        brand=brend,
        Appointment=appointment,
        Class_compress=class_compress,
        Male=male,
        Sock=sock,
        Type_product=type_product,
        Model_type=model_type,
        Size=size,
        stock=1,
        price=5999.00,
        available=True
    )
    product1.Color.add(color_black)

    product2 = Product.objects.create(
        name="Test Product 2",
        slug="test-product-2",
        brand=brend,
        Appointment=appointment,
        Class_compress=class_compress,
        Male=male,
        Sock=sock,
        Type_product=type_product,
        Model_type=model_type,
        Size=size,
        price=6999.00,
        stock=1,
        available=True
    )
    product2.Color.add(color_white)

    product3 = Product.objects.create(
        name="Test Product 3",
        slug="test-product-3",
        brand=brend,
        Appointment=appointment,
        Class_compress=class_compress,
        Male=male,
        Sock=sock,
        Type_product=type_product,
        Model_type=model_type,
        Size=size,
        price=7999.00,
        stock=1,
        available=True
    )
    product3.Color.add(color_red)

    product4 = Product.objects.create(
        name="Test Product 4",
        slug="test-product-4",
        brand=brend,
        Appointment=appointment,
        Class_compress=class_compress,
        Male=male,
        Sock=sock,
        Type_product=type_product,
        Model_type=model_type,
        Size=size,
        price=8999.00,
        stock=1,
        available=True
    )
    product4.Color.add(color_black)

    # Создание галереи для продукта
    gallery1 = Gallery.objects.create(product=product1, image="test1.jpg")
    gallery2 = Gallery.objects.create(product=product1, image="test2.jpg")

    return {
        'country': country,
        'brend': brend,
        'appointment': appointment,
        'male': male,
        'class_compress': class_compress,
        'color': color_black,
        'sock': sock,
        'type_product': type_product,
        'size': size,
        'model_type': model_type,
        'products': [product1, product2, product3, product4],
        'galleries': [gallery1, gallery2]
    }


@pytest.fixture
def cart_request():
    """Создает запрос с сессией для тестов корзины"""
    request = RequestFactory().get('/')
    middleware = SessionMiddleware(get_response=lambda r: None)
    middleware.process_request(request)
    request.session.save()
    return request


@pytest.fixture
def cart_session(cart_request):
    """Фикстура для сессии корзины"""
    return cart_request.session


# Тесты
@pytest.mark.django_db
def test_home_page(client):
    url = reverse('homepage:homepage')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_initialize_cart_clean_session(cart_request):
    cart = Cart(cart_request)
    assert cart.cart == {}


@pytest.mark.django_db
def test_add_cart(test_data, cart_request):
    cart = Cart(cart_request)
    product = test_data['products'][0]
    color = test_data['color']
    size = test_data['size']
    model_type = test_data['model_type']
    images_m = Gallery.objects.filter(product=product)
    cart.add(
        product=product,
        quantity=1,
        size=size,
        color=color,
        m_type=model_type,
        images_m=images_m
    )
    expected_cart_item = {
        # 'product': test_data['products'][0],
        'product_id': '1',
        'color': 'black',
        'images_m': str(images_m),
        'm_type': 'Стандартная',
        'price': '5999.0',
        'quantity': 1,
        'size': '4'
    }
    product_key = cart._generate_product_key(product, size, color, model_type)
    assert cart.cart[product_key] == expected_cart_item


@pytest.mark.django_db
def test_del_cart(test_data, cart_request):
    cart = Cart(cart_request)
    product = test_data['products'][0]
    color = test_data['color']
    size = test_data['size']
    model_type = test_data['model_type']
    images_m = Gallery.objects.filter(product=product)
    cart.add(
        product=product,
        quantity=1,
        size=size,
        color=color,
        m_type=model_type,
        images_m=images_m
    )
    cart.remove(product, size, color, model_type)
    assert cart.cart == {}


@pytest.mark.django_db
def test_count_catalog(test_data):
    catalog_count = Product.objects.count()
    assert catalog_count == 4


@pytest.mark.django_db
def test_catalog(client):
    url = reverse('catalog:catalog')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_catalog_detail(test_data, client):
    product = test_data['products'][0]
    url = reverse('catalog:detail', kwargs={'slug': product.slug})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_create_order(test_data):
    color = test_data['color']
    size = test_data['size']
    model_type = test_data['model_type']
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

    assert form.is_valid()
    order = form.save()
    OrderItem.objects.create(
        order=order,
        product=test_data['products'][0],
        price=5000,
        quantity=1,
        size=size,
        color=color,
        m_type=model_type,
    )
    assert Order.objects.count() == initial_order_count + 1
    assert OrderItem.objects.count() == initial_order_item_count + 1
