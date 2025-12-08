import logging

from cart.cart import Cart
from catalog.models import Color, Model_type, Size
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import get_object_or_404, render

from traning_store.settings import ROBOKASSA_LOGIN, ROBOKASSA_PASSWORD_1
from traning_store.views import generate_payment_link

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .tasks import order_created


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin_detail.html',
                  {'order': order})


logger = logging.getLogger(__name__)


def _create_order_items(order, cart):
    """Упрощенная версия, близкая к вашему исходному коду"""
    order_items = []

    for item in cart:
        # Берем первый найденный размер
        size = None
        if item.get('size'):
            size = Size.objects.filter(name=item['size']).first()

        # Берем первый найденный тип
        m_type = None
        if item.get('m_type'):
            m_type = Model_type.objects.filter(name=item['m_type']).first()

        # Цвет должен быть точно найден
        color = Color.objects.filter(name=item['color']).first()
        if not color:
            # Цвет по умолчанию
            color = Color.objects.get_or_create(
                name='Не указан',
                defaults={'code': '#CCCCCC'}
            )[0]

        order_items.append(OrderItem(
            order=order,
            product=item['product'],
            price=item['price'],
            quantity=item['quantity'],
            size=size,
            color=color,
            m_type=m_type,
        ))

    # Все еще используем bulk_create для скорости
    OrderItem.objects.bulk_create(order_items)


# Вспомогательная функция для подготовки данных формы
def _prepare_initial_form_data(request):
    """Подготовка начальных данных для формы заказа"""
    initial_data = {
        "address": "-",
        "postal_code": "-",
        "city": "-",
        "address_pvz": "-"
    }

    # Добавляем email для авторизованных пользователей
    if request.user.is_authenticated:
        initial_data["email"] = request.user.email
    else:
        initial_data["email"] = ""

    # Добавляем адрес доставки из сессии если есть
    delivery_address = request.session.get('delivery_address')
    if delivery_address:
        initial_data["address_pvz"] = delivery_address

    return initial_data


# Основная функция создания заказа
def order_create(request):
    cart = Cart(request)

    # Проверка пустой корзины
    if not cart:
        return render(request, 'create.html', {
            'form': OrderCreateForm(initial=_prepare_initial_form_data(request)),
            'cart': cart,
            'error': 'Ваша корзина пуста'
        })

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)

                    if cart.coupon:
                        order.coupon = cart.coupon
                        order.discount = cart.coupon.discount

                    if cart.delivery != 0:
                        order.delivery_sum = cart.delivery()

                    order.save()

                    # Создаем OrderItems с оптимизацией
                    _create_order_items(order, cart)

                    logger.info(f'Создан заказ #{order.id} на сумму {order.get_total_cost()}')

            except Exception as e:
                logger.error(f'Ошибка создания заказа: {str(e)}')
                return render(request, 'create.html', {
                    'cart': cart,
                    'form': form,
                    'error': 'Произошла ошибка при создании заказа'
                })

            # Вне транзакции
            cart.clear()
            order_created.delay(order.id)

            pay_link = generate_payment_link(
                merchant_login=ROBOKASSA_LOGIN,
                merchant_password_1=ROBOKASSA_PASSWORD_1,
                cost=order.get_total_cost(),
                number=order.id,
                description='kompressionnyj_trikotazh',
                is_test=0,
                robokassa_payment_url='https://auth.robokassa.ru/Merchant/Index.aspx',
                email=order.email,
            )

            return render(request, 'created.html', {
                'order': order,
                'pay_link': pay_link,
            })

    else:
        # Используем вспомогательную функцию
        form = OrderCreateForm(initial=_prepare_initial_form_data(request))

    return render(request, 'create.html', {
        'cart': cart,
        'form': form,
    })
