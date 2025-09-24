import django_filters

from .models import (Appointment, Brend, Class_compress, Male, Product, Soсk,
                     Type_product)


class ProductFilter(django_filters.FilterSet):
    Appointment = django_filters.ModelChoiceFilter(queryset=Appointment.objects.all(), label='Назначение')
    Sock = django_filters.ModelChoiceFilter(queryset=Soсk.objects.all(), label='Тип носка')
    brand = django_filters.ModelChoiceFilter(queryset=Brend.objects.all(), label='Производитель')
    Class_compress = django_filters.ModelChoiceFilter(queryset=Class_compress.objects.all(), label='Класс компрессии')
    Type_product = django_filters.ModelChoiceFilter(queryset=Type_product.objects.all(), label='Вид изделия')
    Male = django_filters.ModelChoiceFilter(queryset=Male.objects.all(), label='Пол')

    class Meta:
        model = Product
        fields = ['Appointment', 'Sock', 'brand', 'Class_compress', 'Type_product', 'Male']
