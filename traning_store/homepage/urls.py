from django.urls import path

from . import views

app_name = 'homepage'

urlpatterns = [
    path('', views.HomePage.as_view(), name='homepage'),
]
