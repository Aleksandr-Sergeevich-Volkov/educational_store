from celery import shared_task
from django.core.mail import send_mail

from traning_store.settings import EMAIL_HOST_USER

from .models import Order, OrderItem


@shared_task
def order_created(order_id):
    """
    Задача для отправки уведомления о заказе.
    Исправлена генерация URL.
    """
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # Используем ваш домен
    domain = 'kompressionnye-chulki24.ru'

    # Формируем относительный URL для деталей заказа
    order_detail_path = f"/profile/orders/{order_id}/"

    # Формируем URL для входа с параметром next
    login_url = f"https://{domain}/auth/login/"

    # Важно: не используем reverse если он возвращает None
    # Вместо этого формируем URL вручную

    # Кодируем next параметр
    from urllib.parse import quote
    encoded_next = quote(order_detail_path, safe='')

    # Формируем финальную ссылку
    login_with_redirect_url = f"{login_url}?next={encoded_next}"

    # Простая альтернатива без кодирования:
    # login_with_redirect_url = f"{login_url}?next={order_detail_path}"

    # Собираем информацию о товарах
    items_info = []
    for item in order_items:
        size_name = item.size.name if item.size and hasattr(item.size, 'name') else 'не указан'
        color_name = item.color.name if item.color and hasattr(item.color, 'name') else 'не указан'
        m_type_name = item.m_type.name if item.m_type and hasattr(item.m_type, 'name') else 'не указан'

        items_info.append(
            f"- {item.product.name}, "
            f"размер: {size_name}, "
            f"цвет: {color_name}, "
            f"модель: {m_type_name}, "
            f"кол-во: {item.quantity} шт., "
            f"цена: {item.price} руб., "
            f"сумма: {item.get_cost()} руб."
        )

    items_text = "\n".join(items_info)

    subject = f'Заказ №{order_id} успешно оформлен'
    message = f'''Уважаемый(ая) {order.first_name},

Ваш заказ успешно сформирован.

ИНФОРМАЦИЯ О ЗАКАЗЕ:
----------------------------------------
Номер заказа: {order.id}
Дата заказа: {order.created.strftime('%d.%m.%Y H:%M')}
Сумма товаров: {order.get_total_cost()} руб.
Доставка: {order.delivery_sum} руб.
Общая сумма: {float(order.get_total_cost()) + float(order.delivery_sum)} руб.
Адрес пункта выдачи: {order.address_pvz}
Статус оплаты: {"Оплачен" if order.paid else "Ожидает оплаты"}
----------------------------------------

СОСТАВ ЗАКАЗА:
{items_text}
----------------------------------------

КАК ПРОСМОТРЕТЬ ЗАКАЗ:
----------------------------------------
Для просмотра деталей заказа перейдите по ссылке:
{login_with_redirect_url}

Используйте для входа email: {order.email}

После входа вы автоматически перейдете к деталям заказа.
----------------------------------------

ВАЖНО:
• Сохраните номер заказа: {order.id}
----------------------------------------

Спасибо за ваш заказ!
С уважением, команда {domain}
'''

    return send_mail(
        subject,
        message,
        EMAIL_HOST_USER,
        [order.email],
        fail_silently=False
    )
