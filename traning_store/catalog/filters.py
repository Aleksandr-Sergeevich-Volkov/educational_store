import django_filters

from .models import Appointment, Product, Soсk


class ProductFilter(django_filters.FilterSet):
    # Appoitnment = django_filters.CharFilter(field_name='Appoitment', lookup_expr='exact', label='Назначение')
    # Appoitnment = django_filters.ChoiceFilter(choices=Product.Appointment, label='Назначение')
    Appoitnment = django_filters.ModelChoiceFilter(queryset=Appointment.objects.all(), label='Назначение')

    # Sock = django_filters.CharFilter(field_name='Sock', lookup_expr='exact', label='Тип носка')
    Sock = django_filters.ModelChoiceFilter(queryset=Soсk.objects.all(), label='Тип носка')

    class Meta:
        model = Product
        fields = ['Appoitnment', 'Sock']
