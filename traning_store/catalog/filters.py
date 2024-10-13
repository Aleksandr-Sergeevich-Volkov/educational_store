import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    Appointment = django_filters.CharFilter(lookup_expr='icontains')
    Sock = django_filters.CharFilter(lookup_expr='exact')
    #min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    #max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['Appointment', 'Sock' ]