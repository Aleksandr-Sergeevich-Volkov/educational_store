import re

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
        return f'{self.name}'


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
    # ДОБАВИТЬ эти SEO-поля:
    seo_h1 = models.CharField('H1 заголовок', max_length=255, blank=True)
    seo_keywords = models.TextField('Ключевые слова', blank=True)

    # УЛУЧШИТЬ метод save():
    def save(self, *args, **kwargs):
        # Генерация SEO полей если пустые
        if not self.seo_title:
            self.seo_title = self._generate_seo_title()

        if not self.seo_h1:
            self.seo_h1 = self.name  # или кастомная логика

        if not self.seo_description:
            self.seo_description = self._generate_seo_description()

        if not self.seo_alt:
            self.seo_alt = self._generate_seo_alt()

        if not self.seo_keywords:
            self.seo_keywords = self._generate_keywords()

        super().save(*args, **kwargs)

    # ДОБАВИТЬ эти методы:
    def _generate_seo_title(self):
        """Умная генерация title с вариативностью"""
        import random

        # Разные шаблоны для разных типов запросов
        templates = [
            # Коммерческие шаблоны
            lambda: f"{self.name} - купить арт. {self.articul} в Москве | {self.brand}",
            lambda: f"Купить {self.name} {self.brand} арт. {self.articul} цена с доставкой",
            lambda: f"{self.name} {self.brand} арт. {self.articul} - заказать в интернет-магазине",

            # С характеристиками
            lambda: f"{self.name} {self.Class_compress} - купить {self.brand} арт. {self.articul}",
            lambda: f"{self.Type_product} {self.Appointment} {self.brand} - купить арт. {self.articul}",
        ]

        return random.choice(templates)()

    def _generate_seo_description(self):
        """Генерация уникального description для каждого товара"""
        features = self.get_features_dict()

        # Берем 2-3 основные характеристики
        main_features = []
        for key in ['Назначение', 'Класс компрессии', 'Вид изделия']:
            if key in features and features[key]:
                main_features.append(features[key].lower())

        features_text = ", ".join(main_features[:3])

        # Разные варианты описаний
        descriptions = [
            f"Купить {self.name.lower()} {self.brand} арт. {self.articul}. {features_text}. "
            f"Выгодная цена, доставка по Москве и России. Гарантия качества.",

            f"{self.name} {self.brand} - компрессионный трикотаж. {features_text}. "
            f"Артикул: {self.articul}. Закажите онлайн с доставкой.",

            f"Заказать {self.name.lower()} {self.brand} арт. {self.articul}. {features_text}. "
            f"Официальный поставщик, сертифицированная продукция."
        ]

        import random
        description = random.choice(descriptions)

        # Ограничение длины для SEO
        return description[:155] + "..." if len(description) > 160 else description

    def _generate_seo_alt(self):
        """Генерация alt для изображений"""
        return f"{self.name} {self.brand} артикул {self.articul} - фото, характеристики, отзывы"

    def _is_natural_query(self, keyword):
        """Проверяет, выглядит ли запрос естественно"""
        keyword_lower = keyword.lower()

        # 1. Слишком короткие запросы (меньше 2 слов)
        words = keyword_lower.split()
        if len(words) < 2:
            return False

        # 2. ОЧЕНЬ ЖЕСТКИЕ фильтры (только реальный спам)
        hard_filters = [
            'артикул купить',
            'купить артикул',
        ]

        for pattern in hard_filters:
            if pattern in keyword_lower:
                return False

        # 3. Проверка на полную бессмысленность
        meaningful_words = [
            'компрессионные', 'чулки', 'гольфы', 'колготки',
            'варикоз', 'класс', 'компрессии',
            'купить', 'цена', 'заказать'
        ]

        # Хотя бы одно осмысленное слово должно быть
        if not any(word in keyword_lower for word in meaningful_words):
            return False

        return True

    def _generate_keywords(self):
        """Генерация ключевых слов на основе реальных поисковых запросов"""
        keywords = set()

        # Проверяем обязательные поля
        if not self.brand or not self.Type_product:
            return ""

        brand_name = str(self.brand).lower()
        product_type = str(self.Type_product).lower()

        # ИСПРАВЛЕНО: Определяем оба варианта названия для гибкости
        # full_type - как есть из БД (например, "компрессионные чулки")
        # base_type - без "компрессионные" если они есть (например, "чулки")
        if product_type.startswith('компрессионные '):
            full_type = product_type  # "компрессионные чулки"
            base_type = product_type.replace('компрессионные ', '', 1).strip()  # "чулки"
        else:
            full_type = product_type
            base_type = product_type

        # 1. ОСНОВНЫЕ РЕАЛЬНЫЕ ЗАПРОСЫ

        # ИСПРАВЛЕНО: Используем full_type вместо type_name для избежания дублирования
        # Вариант 1: "компрессионные чулки venoteks" (самый частый!)
        keywords.add(f"{full_type} {brand_name}")

        # Вариант 2: "venoteks компрессионные чулки"
        keywords.add(f"{brand_name} {full_type}")

        # ИСПРАВЛЕНО: Добавили варианты без "компрессионные" для разнообразия
        # Вариант 3: "venoteks чулки" (только если base_type отличается)
        if base_type != full_type:
            keywords.add(f"{brand_name} {base_type}")

        # Вариант 4: "чулки venoteks" (только если base_type отличается)
        if base_type != full_type:
            keywords.add(f"{base_type} {brand_name}")

        # 2. ЗАПРОСЫ С ХАРАКТЕРИСТИКАМИ
        if self.Class_compress:
            class_name = str(self.Class_compress).lower()

            # "venoteks компрессионные чулки 2 класс"
            keywords.add(f"{brand_name} {full_type} {class_name}")

            # "компрессионные чулки 2 класса venoteks"
            keywords.add(f"{full_type} {class_name} {brand_name}")

            # "2 класс компрессии venoteks"
            keywords.add(f"{class_name} компрессии {brand_name}")

            # "компрессионные чулки 2 класса"
            keywords.add(f"{full_type} {class_name}")

        # ИСПРАВЛЕНО: Добавили естественные варианты с base_type
        if base_type != full_type:
            keywords.add(f"{base_type} {class_name} {brand_name}")  # "чулки 2 класса venoteks"
            keywords.add(f"{brand_name} {base_type} {class_name}")  # "venoteks чулки 2 класс"

        # 3. ЗАПРОСЫ С НАЗНАЧЕНИЕМ
        if self.Appointment:
            appointment_name = str(self.Appointment).lower()

            # "venoteks от варикоза"
            keywords.add(f"{brand_name} {appointment_name}")

            # "компрессионные чулки venoteks при варикозе"
            keywords.add(f"{full_type} {brand_name} {appointment_name}")

            # "варикоз компрессионные чулки venoteks"
            keywords.add(f"{appointment_name} {full_type} {brand_name}")

            # "компрессионные чулки при варикозе"
            keywords.add(f"{full_type} {appointment_name}")

        # ИСПРАВЛЕНО: Добавили варианты с base_type
        if base_type != full_type:
            keywords.add(f"{base_type} {brand_name} {appointment_name}")  # "чулки venoteks при варикозе"
            keywords.add(f"{appointment_name} {base_type} {brand_name}")  # "варикоз чулки venoteks"

        # 4. КОММЕРЧЕСКИЕ ЗАПРОСЫ
        commercial_words = ['купить', 'цена', 'заказать']

        # ИСПРАВЛЕНО: Расширили базовые комбинации
        commercial_bases = [
            f"{brand_name} {full_type}",
            f"{full_type} {brand_name}",
        ]

        # Добавим base_type варианты если они есть
        if base_type != full_type:
            commercial_bases.extend([
                f"{brand_name} {base_type}",
                f"{base_type} {brand_name}",
            ])

        for base in commercial_bases:
            for action in commercial_words:
                keywords.add(f"{action} {base}")
                # Только для "цена" и "заказать" - обратный порядок
                if action in ['цена', 'заказать']:
                    keywords.add(f"{base} {action}")

        # ИСПРАВЛЕНО: Добавили более естественные коммерческие фразы
        keywords.add(f"сколько стоят {full_type} {brand_name}")
        keywords.add(f"{full_type} {brand_name} с доставкой")
        keywords.add(f"где купить {full_type} {brand_name}")

        # 5. ГЕО-ЗАПРОСЫ (только для Москвы и СПб)
        geo_cities = ['москва', 'санкт-петербург']

        # Только для популярных брендов
        popular_brands = ['orto', 'ergoforma', 'venoteks', 'trives', 'венотэкс', 'luomma_idealista', 'cмоленский трикотаж']
        if brand_name in [b.lower() for b in popular_brands]:
            for city in geo_cities:
                # ИСПРАВЛЕНО: Используем full_type
                keywords.add(f"{full_type} {brand_name} {city}")
                keywords.add(f"купить {full_type} {brand_name} {city}")

                # Добавляем base_type варианты если есть
                if base_type != full_type:
                    keywords.add(f"{base_type} {brand_name} {city}")

        # 6. ЗАПРОСЫ С АРТИКУЛОМ (очень аккуратно!)
        if self.articul:
            articul_clean = self.articul.lower()

            # Заменяем точки и дефисы на пробелы
            articul_clean = re.sub(r'[\.\-]', ' ', articul_clean)
            articul_clean = re.sub(r'\s+', ' ', articul_clean).strip()

            # Проверяем, что артикул имеет смысл
            # Должен содержать буквы и быть не слишком длинным
            has_letters = any(c.isalpha() for c in articul_clean)
            not_too_long = len(articul_clean) <= 20

            if has_letters and not_too_long:
                # ИСПРАВЛЕНО: Добавили артикул к full_type
                keywords.add(f"{full_type} {brand_name} {articul_clean}")

                # Только для коротких артикулов
                if len(articul_clean.split()) <= 3:
                    keywords.add(f"арт {articul_clean} {brand_name}")
                    keywords.add(f"{brand_name} {full_type} арт {articul_clean}")

        # 7. ЦВЕТА (если указаны и это важно)
        if self.pk and hasattr(self, 'Color') and self.Color.exists():
            # Берем только основные цвета
            main_colors = ['черный', 'телесный', 'бежевый', 'белый']
            for color in self.Color.all()[:2]:  # Максимум 2 цвета
                color_name = str(color).lower()
                if color_name in main_colors:
                    # ИСПРАВЛЕНО: Используем full_type
                    keywords.add(f"{color_name} {full_type} {brand_name}")

                    # Добавляем base_type вариант если есть
                    if base_type != full_type:
                        keywords.add(f"{color_name} {base_type} {brand_name}")
                    break

        # 8. ИСПРАВЛЕНО: ДОБАВЛЕНЫ НОВЫЕ КАТЕГОРИИ ЗАПРОСОВ

        # Медицинские запросы
        keywords.add(f"медицинские {base_type} {brand_name}")
        keywords.add(f"лечебный трикотаж {brand_name}")
        keywords.add(f"{full_type} по назначению врача")

        # Вопросные формы
        keywords.add(f"как выбрать {full_type} {brand_name}")
        keywords.add(f"как носить {full_type} {brand_name}")

        # Запросы с отзывами
        keywords.add(f"{brand_name} {full_type} отзывы")
        keywords.add(f"{full_type} {brand_name} качество")

        # Длинные хвостовые запросы
        long_tail_phrases = [
            f"где лучше купить {full_type} {brand_name}",
            f"инструкция по применению {full_type} {brand_name}",
            f"сколько служат {full_type} {brand_name}",
        ]

        for phrase in long_tail_phrases:
            if 2 <= len(phrase.split()) <= 5:
                keywords.add(phrase)

        # 9. ФИЛЬТРАЦИЯ И ОПТИМИЗАЦИЯ
        optimized_keywords = []

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # ИСПРАВЛЕНО: Увеличили максимальную длину до 5 слов для хвостовых запросов
            word_count = len(keyword_lower.split())
            if 2 <= word_count <= 5:
                # Проверяем естественность
                if self._is_natural_query(keyword_lower):
                    # Проверяем, что запрос содержит бренд или тип изделия
                    if brand_name in keyword_lower or base_type in keyword_lower:
                        optimized_keywords.append(keyword_lower)

        # Убираем дубликаты
        seen = set()
        unique_keywords = []

        for kw in optimized_keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        # ИСПРАВЛЕНО: Улучшенная сортировка по важности
        def sort_key(keyword):
            score = 0

            # Высший приоритет: коммерческие запросы
            if any(word in keyword for word in ['купить', 'цена', 'сколько', 'заказать']):
                score -= 50

            # Приоритет: начинается с full_type или brand_name
            if keyword.startswith(full_type) or keyword.startswith(brand_name):
                score -= 20

            # Оптимальная длина (3 слова)
            word_count = len(keyword.split())
            score += abs(word_count - 3) * 5

            # Бонус: содержит город
            if any(city in keyword for city in geo_cities):
                score -= 10

            # Бонус: содержит класс компрессии
            if self.Class_compress and str(self.Class_compress).lower() in keyword:
                score -= 5

            return score

        unique_keywords.sort(key=sort_key)

        # ИСПРАВЛЕНО: Возвращаем 15 лучших ключевых слов
        return ", ".join(unique_keywords[:15])

    def get_features_dict(self):
        """Полный словарь характеристик для SEO"""
        if self.pk:  # или self.id
            colors = ', '.join([str(c) for c in self.Color.all()]) if self.Color.exists() else ''
        else:
            colors = ''
        return {
            'Бренд': str(self.brand) if self.brand else '',
            'Артикул': self.articul,
            'Назначение': str(self.Appointment) if self.Appointment else '',
            'Класс компрессии': str(self.Class_compress) if self.Class_compress else '',
            'Тип носка': str(self.Sock) if self.Sock else '',
            'Вид изделия': str(self.Type_product) if self.Type_product else '',
            'Размер': str(self.Size) if self.Size else '',
            'Модель': str(self.Model_type) if self.Model_type else '',
            'Пол': str(self.Male) if self.Male else '',
            'Цвета': colors
        }


class Gallery(models.Model):
    image = models.ImageField(upload_to='images/')
    main = models.BooleanField(default=False)
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='images')
