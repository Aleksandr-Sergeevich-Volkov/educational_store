from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('catalog/', views.ProductListView.as_view(), name='catalog'),
    path('catalog/<slug:slug>/',
         views.ProductDetailView.as_view(),
         name='detail'),
]
