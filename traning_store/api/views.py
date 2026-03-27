"""
Viewset'ы для API интернет-магазина компрессионного трикотажа
"""
from catalog.models import (Appointment, Brend, Class_compress, Male, Product,
                            Type_product)
from django.db.models import Max, Min, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (AppointmentSerializer, BrandSerializer,
                          ClassCompressSerializer, FiltersDataSerializer,
                          MaleSerializer, ProductDetailSerializer,
                          ProductListSerializer, TypeProductSerializer)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для работы с товарами.
    Поддерживает фильтрацию, поиск и сортировку.
    """
    queryset = Product.objects.filter(available=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'Type_product': ['exact'],
        'brand': ['exact'],
        'Class_compress': ['exact'],
        'Appointment': ['exact'],
        'Male': ['exact'],
        'price': ['gte', 'lte'],
    }
    search_fields = ['name', 'articul', 'brand__name', 'description']
    ordering_fields = ['price', 'created', 'name', '-price']
    ordering = ['-created']

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от действия"""
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def get_queryset(self):
        """Дополнительные фильтры"""
        queryset = super().get_queryset()

        # Фильтр по наличию на складе
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)

        # Фильтр по цвету
        color = self.request.query_params.get('color')
        if color:
            queryset = queryset.filter(Color__name__iexact=color)

        return queryset

    @action(detail=False, methods=['get'], url_path='filters')
    def get_filters_data(self, request):
        """
        Возвращает данные для построения фильтров в каталоге:
        - категории (виды изделий)
        - бренды
        - классы компрессии
        - назначения
        - пол
        - диапазон цен
        """
        # Базовый queryset (только доступные товары)
        base_qs = Product.objects.filter(available=True)

        # Диапазон цен
        price_agg = base_qs.aggregate(min_price=Min('price'), max_price=Max('price'))

        data = {
            'types': TypeProductSerializer(Type_product.objects.all(), many=True).data,
            'brands': BrandSerializer(Brend.objects.all(), many=True).data,
            'compress_classes': ClassCompressSerializer(Class_compress.objects.all(), many=True).data,
            'appointments': AppointmentSerializer(Appointment.objects.all(), many=True).data,
            'males': MaleSerializer(Male.objects.all(), many=True).data,
            'price_min': price_agg['min_price'] or 0,
            'price_max': price_agg['max_price'] or 0,
        }

        serializer = FiltersDataSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='search-suggest')
    def search_suggest(self, request):
        """
        Возвращает подсказки для поиска
        """
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])

        # Поиск по названиям товаров
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(articul__icontains=query)
        )[:10]

        suggestions = []
        for p in products:
            suggestions.append({
                'type': 'product',
                'id': p.id,
                'name': p.name,
                'articul': p.articul,
                'price': str(p.price),
            })

        return Response(suggestions)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API для категорий товаров (виды изделий)"""
    queryset = Type_product.objects.all()
    serializer_class = TypeProductSerializer


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """API для брендов"""
    queryset = Brend.objects.all()
    serializer_class = BrandSerializer


class CompressClassViewSet(viewsets.ReadOnlyModelViewSet):
    """API для классов компрессии"""
    queryset = Class_compress.objects.all()
    serializer_class = ClassCompressSerializer
