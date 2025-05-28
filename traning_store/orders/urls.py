from django.urls import path, re_path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    re_path(r'^create/$', views.order_create, name='order_create'),
    re_path(r'^admin/order/(?P<order_id>\d+)/$', views.admin_order_detail,
            name='admin_order_detail'),
    path('fail/', TemplateView.as_view(template_name='fail.html')),
]
