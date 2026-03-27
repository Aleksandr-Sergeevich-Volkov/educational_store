from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (BrandViewSet, CategoryViewSet, CompressClassViewSet,
                    ProductViewSet)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'compress-classes', CompressClassViewSet, basename='compress-class')

urlpatterns = [
    path('', include(router.urls)),
]
