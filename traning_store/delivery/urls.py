from django.urls import path

from . import views

app_name = "delivery"

urlpatterns = [
    path("cart/delivery", views.delivery_add, name="delivery"),
    path("cart/delivery_cdek", views.delivery_add_cdek, name="delivery_cdek"),
    path("cart/delivery_courier", views.delivery_add_courier, name="delivery_courier"),
]
