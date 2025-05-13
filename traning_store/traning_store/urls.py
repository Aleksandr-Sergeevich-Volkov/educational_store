import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [
    re_path(r'^coupons/', include(('coupons.urls', 'coupons'),
                                  namespace='coupons')),
    re_path(r'^orders/', include(('orders.urls', 'orders'),
                                 namespace='orders')),
    re_path(r'^cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('', include('homepage.urls')),
    path('', include('catalog.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]
# Подключаем дебаг-панель:
if settings.DEBUG:
    #  Добавить к списку urlpatterns список адресов
    #  из приложения debug_toolbar:
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
