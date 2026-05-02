from catalog.models import Color, Model_type, Product, Size
from django.db import models


class CartItem(models.Model):
    """
    Модель для хранения корзины пользователя в боте MAX.
    Использует внешние ключи на модели из catalog.
    """
    user_id = models.CharField(
        'ID пользователя в MAX',
        max_length=100,
        db_index=True,
        help_text='Уникальный идентификатор пользователя в мессенджере MAX'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        'Количество',
        default=1
    )

    # Внешние ключи на существующие справочники из catalog
    size = models.ForeignKey(
        Size,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Размер'
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Цвет'
    )
    model_type = models.ForeignKey(
        Model_type,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Модель'
    )

    # Цена на момент добавления (фиксируется)
    price_at_add = models.DecimalField(
        'Цена при добавлении',
        max_digits=10,
        decimal_places=2,
        help_text='Цена товара в момент добавления в корзину'
    )

    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Товар в корзине (бот)'
        verbose_name_plural = 'Товары в корзине (бот)'
        # У одного пользователя не может быть двух одинаковых товаров
        # с одинаковыми характеристиками
        unique_together = ('user_id', 'product', 'size', 'color', 'model_type')
        ordering = ('-created_at',)

    def __str__(self):
        size_name = self.size.name if self.size else '—'
        color_name = self.color.name if self.color else '—'
        model_name = self.model_type.name if self.model_type else '—'
        return f"{self.user_id}: {self.product.name} x{self.quantity} ({size_name}, {color_name}, {model_name})"

    def get_total_price(self):
        """Общая стоимость позиции"""
        return self.price_at_add * self.quantity

    def get_display_name(self):
        """Форматированное название для отображения в боте"""
        name = self.product.name
        if self.size:
            name += f", {self.size.name}"
        if self.color:
            name += f", {self.color.name}"
        if self.model_type:
            name += f", {self.model_type.name}"
        return name


class FavoriteItem(models.Model):
    """
    Модель для хранения избранных товаров пользователя MAX.
    """
    user_id = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='ID пользователя MAX'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Товар'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Избранный товар'
        verbose_name_plural = 'Избранные товары'
        # Один пользователь не может добавить один товар дважды
        unique_together = ('user_id', 'product')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user_id} - {self.product.name}"
