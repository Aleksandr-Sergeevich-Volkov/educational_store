from cart.forms import CartAddProductForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView
from django_filters.views import FilterView
from orders.models import Order, OrderItem

from .filters import ProductFilter
from .forms import UserForm
from .models import Color, Gallery, Model_type, Product, Size

User = get_user_model()


class ProductListView(FilterView):
    # Указываем модель, с которой работает CBV...
    model = Product
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 10
    template_name = 'product_list.html'
    filterset_class = ProductFilter
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        # Получаем словарь контекста:
        context = super().get_context_data(**kwargs)
        context['images_m'] = Gallery.objects.all()
        context['prod_count'] = Product.objects.aggregate(Count('id'))
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        # Получаем словарь контекста:
        context = super().get_context_data(**kwargs)
        # Добавляем в словарь новый ключ:
        context['images_m'] = Gallery.objects.filter(product=self.object)
        context['colors'] = Color.objects.all()
        context['sizes'] = Size.objects.all()
        context['model_t'] = Model_type.objects.all()
        context['cart_product_form'] = CartAddProductForm()
        # Возвращаем словарь контекста.
        return context


def user_profile(request, username):
    profile = get_object_or_404(User, username=username)
    if request.user == profile and request.user.is_authenticated:
        post_list = Order.objects.values('id').filter(email=request.user.email).order_by('-id')
        orders_item = OrderItem.objects.filter(order__in=post_list).order_by('-order')
        context = {'page_obj': orders_item,
                   'profile': profile, 
                   }
        return render(request, 'blog/profile.html', context)
    else:
        post_list = Order.objects.filter(email=request.user.email)
        context = {'page_obj': post_list,
                   'profile': profile, }
        return render(request, 'blog/profile.html', context)


@login_required
def profile(request, username):
    instance = User.objects.get(username=username)
    form = UserForm(request.POST or None, instance=instance)
    context = {'form': form, }
    if not form.is_valid():
        return render(request, 'blog/user.html', context)
    form.save()
    return redirect('catalog:profile', username=request.user)
