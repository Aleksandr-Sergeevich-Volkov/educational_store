# import logging

from cart.forms import CartAddProductForm
from django.db.models import Count
from django.views.generic import DetailView
from django_filters.views import FilterView

from .filters import ProductFilter
from .models import Color, Gallery, Model_type, Product, Size

# logger = logging.getLogger(__name__)


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
        # logger.warning(context['prod_count']['id__count'])
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
