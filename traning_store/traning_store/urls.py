import debug_toolbar
from catalog.forms import SignUpForm
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from . import views

urlpatterns = [
    re_path(r'^coupons/', include(('coupons.urls', 'coupons'),
                                  namespace='coupons')),
    re_path(r'^orders/', include(('orders.urls', 'orders'),
                                 namespace='orders')),
    re_path(r'^cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('', include('homepage.urls')),
    path('', include('catalog.urls')),
    path('', include('delivery.urls')),
    path('auth/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=SignUpForm,
            success_url=reverse_lazy('homepage:homepage'),
        ),
        name='registration',
    ),
    path('fail/', TemplateView.as_view(template_name='fail.html')),
    path('robokassa/result/', views.result_payment),
    path('robokassa/success/', views.check_success_payment),
    # path('admin/', admin.site.urls),
    # КАСТОМНЫЙ ВХОД ТОЛЬКО ДЛЯ АДМИНКИ
    path(f'{settings.ADMIN_URL}login/', views.admin_login, name='admin_login'),
    path(settings.ADMIN_URL, admin.site.urls),
    path('', views.home, name='home'),
]
# Подключаем дебаг-панель:
if settings.DEBUG:
    #  Добавить к списку urlpatterns список адресов
    #  из приложения debug_toolbar:
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

handler404 = 'homepage.views.handler404'    # myproject.views
handler403 = 'homepage.views.handler403'
handler500 = 'homepage.views.handler500'
