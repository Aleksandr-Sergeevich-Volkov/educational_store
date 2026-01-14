from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    title = models.CharField(
        'Заголовок',
        max_length=256,
    )
    text = models.TextField(
        'Текст',
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name='Город')
    region = models.CharField(max_length=100, verbose_name='Регион')
    country = models.CharField(max_length=50, default='Россия', verbose_name='Страна')

    # Координаты (опционально)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        verbose_name='Широта'
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        verbose_name='Долгота'
    )

    # Флаги
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_popular = models.BooleanField(default=False, verbose_name='Популярный')
    is_default = models.BooleanField(default=False, verbose_name='По умолчанию')

    # Для сортировки
    order = models.IntegerField(default=0, verbose_name='Порядок')

    # Статистика
    detection_count = models.IntegerField(default=0, verbose_name='Количество определений')

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['-is_default', '-is_popular', 'order', 'name']
        indexes = [
            models.Index(fields=['name', 'region']),
            models.Index(fields=['is_active', 'is_popular']),
            models.Index(fields=['detection_count']),
        ]

    def __str__(self):
        return f"{self.name}, {self.region}"

    def save(self, *args, **kwargs):
        # Если это город по умолчанию, снимаем флаг с других
        if self.is_default and self.is_active:
            City.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
