# catalog/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product  # ✅ Только модель Product


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
