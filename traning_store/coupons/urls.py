from django.urls import include, re_path
from . import views


urlpatterns = [
   re_path(r'^apply/$', views.coupon_apply, name='apply'),
]