from django.shortcuts import render
from django.views.generic import ListView
from .models import Product

class ProductListView(ListView):
    # Указываем модель, с которой работает CBV...
    model = Product
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 10 
    template_name = 'product_list.html'
