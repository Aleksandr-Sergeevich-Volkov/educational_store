import logging

from catalog.models import Gallery, Product
from coupons.forms import CouponApplyForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CartAddProductForm

logger = logging.getLogger(__name__)


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    images_m = Gallery.objects.filter(product=product)
    form = CartAddProductForm(request.POST, product=product)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 size=cd['size'],
                 color=cd['color'],
                 m_type=cd['m_type'],
                 images_m=images_m,
                 update_quantity=cd['update'])
    return redirect('cart:cart_detail')


def cart_remove(request, product_id, size, color, m_type):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    # Получаем объекты характеристик (если нужно)
    # Если size, color, m_type - это строки, то используем их как есть
    size_obj = size  # или получите объект Size если нужно
    color_obj = color
    m_type_obj = m_type
    cart.remove(product, size_obj, color_obj, m_type_obj)
    return redirect('cart:cart_detail')


def update_quantity(request):
    if request.method == 'POST':
        cart = Cart(request)
        product_id = request.POST.get('product_id')
        size = request.POST.get('size')
        color = request.POST.get('color')
        m_type = request.POST.get('m_type')
        action = request.POST.get('action')

        product = get_object_or_404(Product, id=product_id)

        # Получаем текущее количество
        current_quantity = cart.get_product_quantity(product, size, color, m_type)

        # Определяем новое количество в зависимости от действия
        if action == 'increase':
            new_quantity = current_quantity + 1
        elif action == 'decrease':
            new_quantity = max(1, current_quantity - 1)
        else:
            # Если изменено вручную в поле input
            new_quantity = int(request.POST.get('quantity', 1))

        # Обновляем количество
        cart.add(
            product=product,
            quantity=new_quantity,
            size=size,
            color=color,
            m_type=m_type,
            update_quantity=True  # Заменяем количество
        )

        return redirect('cart:cart_detail')


""" def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail') """


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'update': True},
            product=item['product'])
    coupon_apply_form = CouponApplyForm()
    images_m = Gallery.objects.all()
    return render(request, 'cart_detail.html',
                  {'cart': cart,
                   'coupon_apply_form': coupon_apply_form,
                   'images_m': images_m,
                   'request': request}
                  )
