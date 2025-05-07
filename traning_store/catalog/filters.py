import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    # Appoitnment = django_filters.CharFilter(field_name='Appoitment', lookup_expr='exact', label='Назначение')
    Appoitnment = django_filters.ChoiceFilter(choices=Product.Appointment, label='Назначение')
    # Sock = django_filters.CharFilter(field_name='Sock', lookup_expr='exact', label='Тип носка')
    Sock = django_filters.ChoiceFilter(choices=Product.Sock, label='Тип носка')

    class Meta:
        model = Product
        fields = ['Appointment', 'Sock']
