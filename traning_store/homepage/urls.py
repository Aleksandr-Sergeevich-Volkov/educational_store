from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'homepage'

urlpatterns = [
    path('', views.HomePage.as_view(), name='homepage'),
    path('<int:pk>/', views.detail_view, name='detail'),
    path('<int:post_id>/comment/',
         views.add_comment, name='add_comment'),
    path('<int:post_id>/edit_comment/<int:comment_id>/',
         views.edit_comment, name='edit_comment'),
    path('<int:post_id>/delete_comment/<int:comment_id>/',
         views.delete_comment, name='delete_comment'),
    path('yandex_445ca9b51fd08dec.html/', TemplateView.as_view(template_name='yandex_445ca9b51fd08dec.html')),
]
