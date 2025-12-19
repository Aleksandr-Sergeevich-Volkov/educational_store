# catalog/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product  # ✅ Только модель Product


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'
    protocol = 'https'  # Не забываем про HTTPS

    # Список имен URL-путей (name из urls.py)
    def items(self):
        return [
            'homepage:homepage',        # Главная страница
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Product.objects.filter(available=True)

    def lastmod(self, obj):
        return obj.updated

    def location(self, obj):
        return reverse('catalog:detail', kwargs={'slug': obj.slug})  # ✅ Товары используют slug
