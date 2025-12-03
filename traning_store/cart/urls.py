from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.cart_detail,
            name='cart_detail'),
    re_path(r'^add/(?P<product_id>\d+)/$',
            views.cart_add,
            name='cart_add'),
    path('update/', views.update_quantity, name='update_quantity'),
    path('remove/<int:product_id>/<str:size>/<str:color>/<str:m_type>/', views.cart_remove, name='cart_remove'),
]
