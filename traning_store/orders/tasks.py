from celery import shared_task
from django.core.mail import send_mail

from traning_store.settings import EMAIL_HOST_USER

from .models import Order, OrderItem


@shared_task
def order_created(order_id):
    """
    Задача для отправки уведомления по электронной почте
    при успешном создании заказа.
    """
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # Собираем информацию о всех товарах в заказе
    items_info = []
    for item in order_items:
        print(item)
        items_info.append(f"{item.product.name}, размер: {item.size.name}, цвет: {item.color}, "
                          f"модель: {item.m_type.name}, кол-во: {item.quantity}, цена: {item.price} руб.")

    # Объединяем информацию о всех товарах
    items_text = "\n".join(items_info)

    subject = f'Заказ № {order_id}'
    message = f'''Уважаемый {order.first_name},

Ваш заказ успешно сформирован.

Состав заказа:
{items_text}

Номер вашего заказа: {order.id}
Сумма вашего заказа: {order.get_total_cost()}
Адрес пункта выдачи: {order.address_pvz}

Спасибо за ваш заказ!'''

    mail_sent = send_mail(subject,
                          message,
                          EMAIL_HOST_USER,
                          [order.email])
    return mail_sent
