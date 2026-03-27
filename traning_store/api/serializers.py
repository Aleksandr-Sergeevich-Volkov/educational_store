"""
Сериализаторы для API интернет-магазина компрессионного трикотажа
"""
from catalog.models import (Appointment, Brend, Class_compress, Color, Country,
                            Gallery, Male, Model_type, Product, Side, Size,
                            SizeDetail, Soсk, Type_product, Wide_hips)
from rest_framework import serializers

# ========== БАЗОВЫЕ СЕРИАЛИЗАТОРЫ (справочники) ==========


class CountrySerializer(serializers.ModelSerializer):
    """Страна производитель"""
    class Meta:
        model = Country
        fields = ['id', 'name', 'code']


class BrandSerializer(serializers.ModelSerializer):
    """Бренд с информацией о стране"""
    country = CountrySerializer(source='country_brand', read_only=True)

    class Meta:
        model = Brend
        fields = ['id', 'name', 'country', 'size_table_image']


class AppointmentSerializer(serializers.ModelSerializer):
    """Назначение (при варикозе, для спорта и т.д.)"""
    class Meta:
        model = Appointment
        fields = ['id', 'name']


class MaleSerializer(serializers.ModelSerializer):
    """Пол (мужской/женский/унисекс)"""
    class Meta:
        model = Male
        fields = ['id', 'name']


class ColorSerializer(serializers.ModelSerializer):
    """Цвет товара"""
    class Meta:
        model = Color
        fields = ['id', 'name', 'color']


class ClassCompressSerializer(serializers.ModelSerializer):
    """Класс компрессии (1, 2, 3 класс)"""
    class Meta:
        model = Class_compress
        fields = ['id', 'name']


class SockSerializer(serializers.ModelSerializer):
    """Тип носка (открытый/закрытый мыс)"""
    class Meta:
        model = Soсk
        fields = ['id', 'name']


class TypeProductSerializer(serializers.ModelSerializer):
    """Вид изделия (гольфы, чулки, колготки)"""
    class Meta:
        model = Type_product
        fields = ['id', 'name', 'description']


class ModelTypeSerializer(serializers.ModelSerializer):
    """Модель изделия"""
    brand = BrandSerializer(read_only=True)

    class Meta:
        model = Model_type
        fields = ['id', 'name', 'brand', 'description']


class WideHipsSerializer(serializers.ModelSerializer):
    """Широкое бедро (специальная модель)"""
    class Meta:
        model = Wide_hips
        fields = ['id', 'name']


class SideSerializer(serializers.ModelSerializer):
    """Сторона (левая/правая для индивидуальных изделий)"""
    class Meta:
        model = Side
        fields = ['id', 'name']


# ========== РАЗМЕРЫ И ДЕТАЛИ ==========

class SizeDetailSerializer(serializers.ModelSerializer):
    """Детали размера с диапазонами обхватов"""
    ankle_range = serializers.SerializerMethodField()
    calf_range = serializers.SerializerMethodField()
    under_knee_range = serializers.SerializerMethodField()
    mid_thigh_range = serializers.SerializerMethodField()
    upper_thigh_range = serializers.SerializerMethodField()

    class Meta:
        model = SizeDetail
        fields = [
            'id', 'size',
            'ankle_range', 'calf_range', 'under_knee_range',
            'mid_thigh_range', 'upper_thigh_range'
        ]

    def get_ankle_range(self, obj):
        return obj.get_range_display('ankle_circumference')

    def get_calf_range(self, obj):
        return obj.get_range_display('calf_circumference')

    def get_under_knee_range(self, obj):
        return obj.get_range_display('circumference_under_knee')

    def get_mid_thigh_range(self, obj):
        return obj.get_range_display('mid_thigh_circumference')

    def get_upper_thigh_range(self, obj):
        return obj.get_range_display('Upper_thigh_circumference')


class SizeSerializer(serializers.ModelSerializer):
    """Размер с привязкой к бренду и деталями"""
    details = SizeDetailSerializer(source='sizedetail', read_only=True)
    brand = BrandSerializer(read_only=True)

    class Meta:
        model = Size
        fields = ['id', 'name', 'brand', 'details']


# ========== ГАЛЕРЕЯ ==========

class GallerySerializer(serializers.ModelSerializer):
    """Изображения товара"""
    class Meta:
        model = Gallery
        fields = ['id', 'image', 'main', 'type_product']


# ========== ТОВАРЫ (ОСНОВНЫЕ) ==========

class ProductListSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    Type_product = TypeProductSerializer(read_only=True)
    Class_compress = ClassCompressSerializer(read_only=True)
    colors = ColorSerializer(source='Color', many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    price_formatted = serializers.SerializerMethodField()
    availability_text = serializers.SerializerMethodField()
    can_order = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'articul',
            'price', 'price_formatted', 'stock',
            'brand', 'Type_product', 'Class_compress',
            'colors', 'main_image', 'availability_text', 'can_order'
        ]

    def get_main_image(self, obj):
        main_image = obj.images.filter(main=True).first()
        if main_image:
            return main_image.image.url
        first_image = obj.images.first()
        return first_image.image.url if first_image else None

    def get_price_formatted(self, obj):
        return f"{obj.price:,.0f} ₽".replace(',', ' ')

    def get_availability_text(self, obj):
        if not obj.available:
            return "Снят с продажи"
        elif obj.stock == 0:
            return "Под заказ"
        elif obj.stock <= 3:
            return f"Осталось {obj.stock} шт."
        return "В наличии"

    def get_can_order(self, obj):
        return obj.available


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной карточки товара
    Используется при открытии конкретного товара
    """
    # Связанные данные
    brand = BrandSerializer(read_only=True)
    type_product = TypeProductSerializer(read_only=True)
    class_compress = ClassCompressSerializer(read_only=True)
    appointment = AppointmentSerializer(read_only=True)
    male = MaleSerializer(read_only=True)
    sock = SockSerializer(read_only=True)
    model_type = ModelTypeSerializer(read_only=True)
    wide_hips = WideHipsSerializer(read_only=True)
    side = SideSerializer(read_only=True)
    size = SizeSerializer(read_only=True)
    colors = ColorSerializer(source='Color', many=True, read_only=True)
    images = GallerySerializer(many=True, read_only=True)

    # Вычисляемые поля
    size_recommendation = serializers.SerializerMethodField()
    price_formatted = serializers.SerializerMethodField()
    delivery_info = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()
    expected_delivery = serializers.SerializerMethodField()

    # ... остальные методы ...

    def get_availability(self, obj):
        if not obj.available:
            return {
                'code': 'discontinued',
                'text': 'Товар снят с продажи',
                'button_text': 'Сообщить о поступлении',
                'button_enabled': True
            }
        elif obj.stock == 0:
            return {
                'code': 'preorder',
                'text': 'Товар под заказ',
                'button_text': 'Оформить предзаказ',
                'button_enabled': True
            }
        return {
            'code': 'in_stock',
            'text': 'В наличии',
            'button_text': 'Добавить в корзину',
            'button_enabled': True
        }

    def get_expected_delivery(self, obj):
        if obj.stock > 0:
            return {
                'min_days': 1,
                'max_days': 3,
                'text': '1-3 дня'
            }
        return {
            'min_days': 5,
            'max_days': 10,
            'text': '5-10 дней (под заказ)'
        }

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'articul', 'code',
            'price', 'price_formatted', 'stock', 'available',
            'brand', 'type_product',
            'class_compress', 'appointment', 'male', 'sock',
            'model_type', 'wide_hips', 'side', 'size',
            'colors', 'images', 'size_recommendation',
            'delivery_info', 'features', 'seo_title', 'seo_description',
            'expected_delivery', 'availability'
        ]

    def get_price_formatted(self, obj):
        """Форматирует цену для отображения"""
        return f"{obj.price:,.0f} ₽".replace(',', ' ')

    def get_size_recommendation(self, obj):
        """
        Возвращает информацию для подбора размера
        На основе данных из SizeDetail
        """
        if obj.Size and hasattr(obj.Size, 'sizedetail'):
            detail = obj.Size.sizedetail
            return {
                'ankle': detail.get_range_display('ankle_circumference'),
                'calf': detail.get_range_display('calf_circumference'),
                'under_knee': detail.get_range_display('circumference_under_knee'),
                'mid_thigh': detail.get_range_display('mid_thigh_circumference'),
                'upper_thigh': detail.get_range_display('Upper_thigh_circumference'),
            }
        return None

    def get_delivery_info(self, obj):
        """Информация о доставке (можно расширить)"""
        return {
            'available': True,
            'delivery_time': '1-3 дня',
            'delivery_price': 'от 0 ₽',
            'pickup_available': True
        }

    def get_features(self, obj):
        """Собирает все характеристики товара в словарь"""
        features = {}

        if obj.brand:
            features['Бренд'] = obj.brand.name
        if obj.articul:
            features['Артикул'] = obj.articul
        if obj.Appointment:
            features['Назначение'] = obj.Appointment.name
        if obj.Class_compress:
            features['Класс компрессии'] = obj.Class_compress.name
        if obj.Sock:
            features['Тип носка'] = obj.Sock.name
        if obj.Type_product:
            features['Вид изделия'] = obj.Type_product.name
        if obj.Male:
            features['Пол'] = obj.Male.name
        if obj.Model_type:
            features['Модель'] = obj.Model_type.name
        if obj.Wide_hips:
            features['Широкое бедро'] = obj.Wide_hips.name
        if obj.Size:
            features['Размер'] = obj.Size.name

        # Цвета
        colors = obj.Color.all()
        if colors.exists():
            features['Цвета'] = ', '.join([c.name for c in colors])

        return features


# ========== КОРЗИНА И ЗАКАЗЫ (для будущего расширения) ==========

class CartItemSerializer(serializers.Serializer):
    """Позиция в корзине"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=99)
    size_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_product_id(self, value):
        """Проверяет, существует ли товар"""
        if not Product.objects.filter(id=value, available=True).exists():
            raise serializers.ValidationError("Товар не найден или недоступен")
        return value


class OrderCreateSerializer(serializers.Serializer):
    """Создание заказа"""
    user_id = serializers.CharField(max_length=255)  # chat_id из MAX
    items = CartItemSerializer(many=True)
    delivery_type = serializers.ChoiceField(choices=['courier', 'pickup', 'post'])
    delivery_address = serializers.CharField(max_length=500, required=False, allow_blank=True)
    comment = serializers.CharField(max_length=500, required=False, allow_blank=True)
    contact_name = serializers.CharField(max_length=255)
    contact_phone = serializers.CharField(max_length=20)
    contact_email = serializers.EmailField(required=False, allow_blank=True)

    def validate(self, data):
        """Проверяет наличие всех товаров"""
        for item in data['items']:
            product = Product.objects.get(id=item['product_id'])
            if product.stock < item['quantity']:
                raise serializers.ValidationError(
                    f"Товар '{product.name}' доступен в количестве {product.stock} шт."
                )
        return data


# ========== ФИЛЬТРЫ И НАВИГАЦИЯ ==========

class FiltersDataSerializer(serializers.Serializer):
    """Данные для фильтров в каталоге"""
    types = TypeProductSerializer(many=True)
    brands = BrandSerializer(many=True)
    compress_classes = ClassCompressSerializer(many=True)
    appointments = AppointmentSerializer(many=True)
    males = MaleSerializer(many=True)
    price_min = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_max = serializers.DecimalField(max_digits=10, decimal_places=2)
