from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'homepage'

urlpatterns = [
    path('', views.HomePage.as_view(), name='homepage'),
    path('<int:pk>/', views.detail_view, name='detail'),
    path('yandex_445ca9b51fd08dec.html/', TemplateView.as_view(template_name='yandex_445ca9b51fd08dec.html')),
]
