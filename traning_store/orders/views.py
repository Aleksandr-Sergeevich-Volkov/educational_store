from cart.cart import Cart
from catalog.models import Color, Model_type, Size
from django.contrib.admin.views.decorators import staff_member_required
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


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            if cart.delivery != 0:
                order.delivery_sum = cart.delivery()
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'],
                                         size=Size.objects.get(name=item['size']),
                                         color=Color.objects.get(name=item['color']),
                                         m_type=Model_type.objects.get(name=item['m_type'])
                                         )
            # очистка корзины
            cart.clear()
            # запуск асинхронной задачи
            order_created.delay(order.id)
            pay_link = generate_payment_link(merchant_login=ROBOKASSA_LOGIN,
                                             merchant_password_1=ROBOKASSA_PASSWORD_1,
                                             cost=order.get_total_cost(),
                                             number=order.id,
                                             description='kompressionnyj_trikotazh',
                                             is_test=0,
                                             robokassa_payment_url='https://auth.robokassa.ru/Merchant/Index.aspx',
                                             email=order.email,)
            context = {'order': order,
                       'pay_link': pay_link,
                       }
            return render(request, 'created.html', context)
    else:
        delivery_address = request.session.get('delivery_address')
        if request.user.is_authenticated and delivery_address:
            email = request.user.email
            form = OrderCreateForm(initial={"email": email,
                                   "address_pvz": request.session['delivery_address'],
                                            "address": "-", "postal_code": "-", "city": "-"})
        elif request.user.is_authenticated:
            email = request.user.email
            form = OrderCreateForm(initial={"email": email,
                                   "address_pvz": "-",
                                            "address": "-", "postal_code": "-", "city": "-"})
        elif request.session.get('delivery_address') is not None:
            form = OrderCreateForm(initial={"email": "-",
                                   "address_pvz": request.session['delivery_address'],
                                            "address": "-", "postal_code": "-", "city": "-"})
        else:
            form = OrderCreateForm(initial={"address_pvz": "-",
                                            "address": "-", "postal_code": "-", "city": "-"})
    return render(request, 'create.html',
                  {'cart': cart, 'form': form, })
