from django.shortcuts import render,get_object_or_404
from cart.forms import CartAddProductForm
from django.views.generic import DetailView
from .models import Product, Gallery, Color, Size, Model_type
from .filters import ProductFilter
from django_filters.views import FilterView
from django.urls import reverse
from django.db.models import Count
import logging
logger = logging.getLogger(__name__)


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
    #queryset = Product.objects.values('name', 'image','slug','brand__name')
    """ queryset = Product.objects.all()
    #my_product = get_object_or_404(Product, id=id)
    #images_m = Gallery.objects.all()
    images =  [Gallery.objects.filter(product=item) for item in queryset]
    images_m=[image.values() for image in images]
    context = {
        #'product': queryset,
        'images_m': images_m
    } """
    """ def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Product.objects.all())
        return super().get(request, *args, **kwargs)"""
    
    def get_context_data(self, **kwargs):
        # Получаем словарь контекста:
        context = super().get_context_data(**kwargs)        
        context['images_m'] = Gallery.objects.all()
        context['prod_count'] = Product.objects.aggregate(Count('id')) 
        logger.warning(context['prod_count']['id__count'])                
        return context  

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'  
    slug_url_kwarg = 'slug'
    """ def get_object(self):
        object = super(ProductDetailView, self).get_object()        
        return object.images.all()
    images_m = get_object(self)
    context = {
        'product': queryset,
        #'images_m': images_m
    }
    logger.warning(queryset)  """
    
    def get_context_data(self, **kwargs):
        # Получаем словарь контекста:
        context = super().get_context_data(**kwargs)
        # Добавляем в словарь новый ключ:
        #context['images_m'] = Gallery.objects.values('image','product').filter(product=self.object)
        context['images_m'] = Gallery.objects.filter(product=self.object)
        context['colors'] = Color.objects.all()
        context['sizes'] = Size.objects.all()
        context['model_t'] = Model_type.objects.all()
        context['cart_product_form'] = CartAddProductForm()
        # Возвращаем словарь контекста.
        #logger.warning([image for image in context['images_m']])
        #logger.warning([context['images_m']])
        return context 
