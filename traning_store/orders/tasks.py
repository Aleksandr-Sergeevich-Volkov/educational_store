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
    subject = 'Order nr. {}'.format(order_id)
    message = 'Dear {},\n\nYou have successfully placed an order.\
                Your order id is {}.'.format(order.first_name,
                                             order.id)
    mail_sent = send_mail(subject,
                          message,
                          EMAIL_HOST_USER,
                          [order.email])
    return mail_sent
