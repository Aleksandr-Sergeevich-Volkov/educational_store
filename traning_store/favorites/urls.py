from django.urls import path

from . import views

app_name = "favorites"

urlpatterns = [
    # Простой toggle без JS (как корзина)
    path("toggle/<int:product_id>/", views.toggle_favorite, name="toggle"),
    # Список избранного
    path("", views.favorites_list, name="list"),
    # Очистка
    path("clear/", views.clear_favorites, name="clear"),
]
