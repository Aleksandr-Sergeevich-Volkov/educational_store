from django.contrib.sitemaps.views import sitemap
from django.urls import path

from . import views
from .sitemaps import ArticleSitemap, ProductSitemap, StaticViewSitemap

app_name = 'catalog'

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'articles': ArticleSitemap,  # Добавляем статьи
}

urlpatterns = [
    path('catalog/', views.ProductListView.as_view(), name='catalog'),
    path('catalog/<slug:slug>/',
         views.ProductDetailView.as_view(),
         name='detail'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('profile/<username>/',
         views.user_profile, name='profile'),
    path('profile/orders/<int:order_id>/',
         views.user_order_detail, name='user_order_detail'),
]
