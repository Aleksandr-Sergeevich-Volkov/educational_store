from celery import shared_task
from django.core.mail import send_mail

from traning_store.settings import EMAIL_HOST_USER

from .models import Order


@shared_task
def order_created(order_id):
    """
    Задача для отправки уведомления по электронной почте
    при успешном создании заказа.
    """
    order = Order.objects.get(id=order_id)
    subject = 'Заказ №. {}'.format(order_id)
    message = 'Уважаемый {},Ваш заказ успешео сформирован.\
                Ваш заказ номер: {}.Адрес пункта выдачи: {}'.format(order.first_name,
                                                                    order.id, order.address_pvz)
    mail_sent = send_mail(subject,
                          message,
                          EMAIL_HOST_USER,
                          [order.email])
    return mail_sent
