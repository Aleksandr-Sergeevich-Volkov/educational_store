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


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


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
