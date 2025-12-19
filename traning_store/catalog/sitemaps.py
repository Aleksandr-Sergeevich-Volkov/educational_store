# catalog/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from homepage.models import Post

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
        return reverse('catalog:detail', kwargs={'slug': obj.slug})


# НОВЫЙ КЛАСС ДЛЯ СТАТЕЙ
class ArticleSitemap(Sitemap):
    changefreq = "monthly"  # Статьи реже обновляются
    priority = 0.7  # Приоритет ниже, чем у товаров
    protocol = 'https'

    def items(self):
        # Возвращаем QuerySet опубликованных статей
        return Post.objects.all()

    def lastmod(self, obj):
        # Используем дату последнего изменения
        return obj.text or obj.title

    def location(self, obj):
        # Генерируем URL с параметром pk
        return reverse('homepage:detail', kwargs={'pk': obj.pk})
