from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('catalog/', views.ProductListView.as_view(), name='catalog'),
    path('catalog/<slug:slug>/',
         views.ProductDetailView.as_view(),
         name='detail'),
    path('profile/<username>/',
         views.user_profile, name='profile'),
    path('profile/orders/<int:order_id>/',
         views.user_order_detail, name='user_order_detail'),
]
