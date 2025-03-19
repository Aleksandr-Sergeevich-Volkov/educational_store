from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('catalog/', views.ProductListView.as_view(),name='catalog'),
<<<<<<< HEAD
    path('catalog/<slug:slug>/', views.ProductDetailView.as_view(),name='detail'),
=======
>>>>>>> 0295487ebcd6703410438ae8a892e0c32d23850d
]