from django.contrib.sitemaps.views import sitemap
from django.urls import path

from . import views
from .sitemaps import ProductSitemap

app_name = 'catalog'

sitemaps = {
    'products': ProductSitemap,
}

urlpatterns = [
    path('catalog/', views.ProductListView.as_view(), name='catalog'),
    path('catalog/<slug:slug>/',
         views.ProductDetailView.as_view(),
         name='detail'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('profile/<username>/',
         views.user_profile, name='profile'),
    path('profile/orders/<int:order_id>/',
         views.user_order_detail, name='user_order_detail'),
]
