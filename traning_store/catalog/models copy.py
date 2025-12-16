from django.contrib.postgres.fields import IntegerRangeField
from django.db import models

from traning_store.constant import COLOR_LEN, MEASURE_LEN, TITLE_LEN


class Country(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)
    code = models.CharField('Код', max_length=TITLE_LEN)

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.code}'


class Brend(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)
    country_brand = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
    )
    size_table_image = models.ImageField(
        'Изображение таблицы размеров',
        upload_to='brands/size_tables/',
        blank=True,
        null=True,
        help_text='Загрузите изображение с таблицей размеров для этого бренда'
    )

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.country_brand}'


class Appointment(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)

    class Meta:
        verbose_name = 'Назначение'
        verbose_name_plural = 'Назначения'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Male(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)

    class Meta:
        verbose_name = 'Пол'
        verbose_name_plural = 'Пол'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Color(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)
    color = models.CharField(
        'Цветовой HEX-код',
        unique=True,
        max_length=COLOR_LEN,
    )

    class Meta:
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвет'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Class_compress(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)

    class Meta:
        verbose_name = 'Класс компрессии'
        verbose_name_plural = 'Класс компрессии'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Soсk(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)

    class Meta:
        verbose_name = 'Носок'
        verbose_name_plural = 'Носок'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Type_product(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)

    class Meta:
        verbose_name = 'Вид изделия'
        verbose_name_plural = 'Вид изделия'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Size(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)
    brand = models.ForeignKey(
        Brend,  # Связь с брендом
        on_delete=models.CASCADE,
        verbose_name='Бренд'
    )

    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размер'
        ordering = ('name',)

    def __str__(self):
        return f'{self.brand.name} - {self.name}'


class SizeDetail(models.Model):
    size = models.ForeignKey(
        Size,  # Связь с размером
        on_delete=models.CASCADE,
        verbose_name='Детали размера'
    )
    ankle_circumference = IntegerRangeField(
        verbose_name='Обхват щиколотки (см)'
    )

    calf_circumference = IntegerRangeField(
        verbose_name='Обхват икры (см)'
    )

    circumference_under_knee = IntegerRangeField(
        verbose_name='Обхват под коленом (см)'
    )

    mid_thigh_circumference = IntegerRangeField(
        verbose_name='Обхват середины бедра (см)'
    )

    Upper_thigh_circumference = IntegerRangeField(
        verbose_name='Обхват бедра верхний (см)'
    )

    class Meta:
        verbose_name = 'Детали размера'
        verbose_name_plural = 'Детали размеров'

    def is_measurement_in_range(self, field_name, value):
        """Проверяет, входит ли измерение в диапазон"""
        try:
            range_value = getattr(self, field_name)
            if range_value:
                return range_value.lower <= value <= range_value.upper
            return False
        except AttributeError:
            return False

    def get_range_display(self, field_name):
        """Возвращает диапазон в формате '18-20'"""
        range_value = getattr(self, field_name)
        if range_value:
            return f"{range_value.lower}-{range_value.upper}"
        return "-"

    def __str__(self):
        return f"Детали для {self.size}"


class Model_type(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)
    brand = models.ForeignKey(
        Brend,  # Связь с брендом
        on_delete=models.CASCADE,
        verbose_name='Бренд'
    )
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модель'
        ordering = ('name',)

    def __str__(self):
        return f"{self.brand.name} - {self.name}"


class Wide_hips(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)

    class Meta:
        verbose_name = 'Широкое бедро'
        verbose_name_plural = 'Широкое бедро'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Side(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)

    class Meta:
        verbose_name = 'Строна'
        verbose_name_plural = 'Сторона'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Product(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)
    brand = models.ForeignKey(
        Brend,
        on_delete=models.CASCADE
    )
    Appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE
    )
    Male = models.ForeignKey(
        Male,
        on_delete=models.CASCADE
    )
    Color = models.ManyToManyField(  # Изменили имя на множественное число
        Color,
        verbose_name='Цвета'
    )
    Class_compress = models.ForeignKey(
        Class_compress,
        on_delete=models.CASCADE
    )
    Sock = models.ForeignKey(
        Soсk,
        on_delete=models.CASCADE
    )
    Type_product = models.ForeignKey(
        Type_product,
        on_delete=models.CASCADE
    )
    Size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
    )
    Model_type = models.ForeignKey(
        Model_type,
        on_delete=models.CASCADE,
    )
    Wide_hips = models.ForeignKey(
        Wide_hips,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    Side = models.ForeignKey(
        Side,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="URL",
    )

    articul = models.CharField('Артикул', max_length=MEASURE_LEN, default='P280')
    code = models.CharField('Код товара', max_length=MEASURE_LEN, default='51723')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # новые SEO-поля
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    seo_alt = models.CharField(max_length=255, blank=True)  # alt для изображений

    def save(self, *args, **kwargs):
        if not self.seo_title:
            self.seo_title = f"{self.name} артикул: {self.articul} - купить в Москве"
        if not self.seo_description:
            self.seo_description = f"Купить {self.name} артикул: {self.articul} по выгодной цене. Компрессионный трикотаж с доставкой."
        if not self.seo_alt:
            self.seo_alt = f"{self.name} артикул: {self.articul} - компрессионный трикотаж"
        super().save(*args, **kwargs)

    def get_features(self):
        """Генерация описания характеристик для SEO"""
        features = []
        if hasattr(self, 'compression_class'):
            features.append(f"{self.Class_compress} класс компрессии")
        if hasattr(self, 'sock_type'):
            features.append(f"{self.Sock} носок")
        return ". ".join(features)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.brand}'


class Gallery(models.Model):
    image = models.ImageField(upload_to='images/')
    main = models.BooleanField(default=False)
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='images')
