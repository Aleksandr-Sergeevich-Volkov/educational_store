from cart.forms import CartAddProductForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView
from django_filters.views import FilterView
from orders.models import Order, OrderItem

from traning_store.settings import ROBOKASSA_LOGIN, ROBOKASSA_PASSWORD_1
from traning_store.views import generate_payment_link

from .filters import ProductFilter
from .forms import UserForm
from .models import Color, Gallery, Model_type, Product, Size

User = get_user_model()


class ProductListView(FilterView):
    model = Product
    ordering = 'id'
    paginate_by = 4
    template_name = 'product_list.html'
    filterset_class = ProductFilter
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related(models.Prefetch(
            'images',
            queryset=Gallery.objects.filter(main=True),
            to_attr='main_images'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_qs = self.filterset.qs
        context['prod_count'] = filtered_qs.aggregate(Count('id'))
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в словарь новый ключ:
        context['images_m'] = Gallery.objects.filter(product=self.object)
        context['colors'] = Color.objects.all()
        context['sizes'] = Size.objects.all()
        context['model_t'] = Model_type.objects.all()
        context['cart_product_form'] = CartAddProductForm()
        return context


def user_profile(request, username):
    profile = get_object_or_404(User, username=username)
    if request.user == profile and request.user.is_authenticated:
        orders = Order.objects.values('id', 'created', 'address_pvz', 'paid').filter(email=request.user.email).order_by('-id')
        context = {'orders': orders,
                   'profile': profile,
                   }
        return render(request, 'blog/profile.html', context)
    else:
        context = {'orders': orders,
                   'profile': profile, }
        return render(request, 'blog/profile.html', context)


def user_order_detail(request, order_id):
    profile = get_object_or_404(User, username=request.user)
    order = get_object_or_404(Order, id=order_id)
    if order.paid is False and request.user == profile and request.user.is_authenticated:
        pay_link = generate_payment_link(merchant_login=ROBOKASSA_LOGIN,
                                         merchant_password_1=ROBOKASSA_PASSWORD_1,
                                         cost=order.get_total_cost(),
                                         number=order.id,
                                         description='kompressionnyj_trikotazh',
                                         is_test=0,
                                         robokassa_payment_url='https://auth.robokassa.ru/Merchant/Index.aspx',
                                         email=order.email,)
        order_item = OrderItem.objects.filter(order=order_id)
        context = {'order_item': order_item,
                   'pay_link': pay_link,
                   'order': order,
                   }
        return render(request, 'blog/user_orders_detail.html', context)
    else:
        order_item = OrderItem.objects.filter(order=order_id)
        context = {'order_item': order_item,
                   'order': order,
                   }
        return render(request, 'blog/user_orders_detail.html', context)


@login_required
def profile(request, username):
    instance = User.objects.get(username=username)
    form = UserForm(request.POST or None, instance=instance)
    context = {'form': form, }
    if not form.is_valid():
        return render(request, 'blog/user.html', context)
    form.save()
    return redirect('catalog:profile', username=request.user)
