from django.shortcuts import render
from django.views.generic import ListView
from .models import Product
from .filters import ProductFilter
from django_filters.views import FilterView

class ProductListView(FilterView):
    # Указываем модель, с которой работает CBV...
    model = Product
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 10 
    template_name = 'product_list.html'
    filterset_class = ProductFilter
