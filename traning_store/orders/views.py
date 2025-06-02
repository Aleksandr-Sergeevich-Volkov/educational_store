from cart.cart import Cart
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render

from traning_store.robokassa import generate_payment_link
from traning_store.settings import ROBOKASSA_LOGIN, ROBOKASSA_PASSWORD_U1

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .tasks import order_created


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin_detail.html',
                  {'order': order})


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # очистка корзины
            cart.clear()
            # запуск асинхронной задачи
            order_created.delay(order.id)
            pay_link = generate_payment_link(merchant_login=ROBOKASSA_LOGIN,
                                             merchant_password_1=ROBOKASSA_PASSWORD_U1,
                                             cost=order.get_total_cost(),
                                             number=order.id,
                                             description='kompressionnyj_trikotazh',
                                             is_test=1,
                                             robokassa_payment_url='https://auth.robokassa.ru/Merchant/Index.aspx',)
            context = {'order': order,
                       'pay_link': pay_link,
                       }
            return render(request, 'created.html', context)
    else:
        if request.user.is_authenticated:
            email = request.user.email
            form = OrderCreateForm(initial={"email": email})
        else:
            form = OrderCreateForm()
    return render(request, 'create.html',
                  {'cart': cart, 'form': form})
