from django.urls import path

from . import views

app_name = 'max_bot'

urlpatterns = [
    path('webhook/', views.max_webhook, name='webhook'),
]
