from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (Appointment, Brend, Class_compress, Color, Country,
                     Gallery, Male, Model_type, Product, Side, Size,
                     SizeDetail, Soсk, Type_product, Wide_hips)

admin.site.register(Country)
admin.site.register(Appointment)
admin.site.register(Male)
admin.site.register(Color)
admin.site.register(Class_compress)
admin.site.register(Soсk)
admin.site.register(Type_product)
admin.site.register(Wide_hips)
admin.site.register(Side)
admin.site.register(Model_type)
admin.site.register(Gallery)


@admin.register(Brend)
class BrendAdmin(admin.ModelAdmin):
    list_display = ['name', 'country_brand', 'has_size_table']
    list_filter = ['country_brand']
    search_fields = ['name']

    def has_size_table(self, obj):
        return bool(obj.size_table_image)
    has_size_table.boolean = True
    has_size_table.short_description = 'Есть таблица размеров'

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'country_brand')
        }),
        ('Таблица размеров', {
            'fields': ('size_table_image',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand']
    list_filter = ['brand']
    search_fields = ['name', 'brand__name']


@admin.register(SizeDetail)
class SizeDetailAdmin(admin.ModelAdmin):
    list_display = ['size', 'ankle_display', 'calf_display', 'mid_thigh_display']
    list_filter = ['size__brand']
    search_fields = ['size__name', 'size__brand__name']

    def ankle_display(self, obj):
        return obj.get_range_display('ankle_circumference')
    ankle_display.short_description = 'Щиколотка'

    def calf_display(self, obj):
        return obj.get_range_display('calf_circumference')
    calf_display.short_description = 'Икра'

    def mid_thigh_display(self, obj):
        return obj.get_range_display('mid_thigh_circumference')
    mid_thigh_display.short_description = 'Середина бедра'

    def get_fields(self, request, obj=None):
        fields = ['size']

        if obj and obj.size.brand:
            brand_name = obj.size.brand.name.lower()
            if 'venoteks' in brand_name:
                fields.extend([
                    'ankle_circumference', 'calf_circumference', 'mid_thigh_circumference'
                ])
            elif 'orto' in brand_name:
                fields.extend([
                    'ankle_circumference', 'calf_circumference', 'circumference_under_knee',
                    'mid_thigh_circumference', 'Upper_thigh_circumference'
                ])
            else:
                # По умолчанию показываем все поля
                fields.extend([
                    'ankle_circumference', 'calf_circumference', 'mid_thigh_circumference',
                    'circumference_under_knee', 'Upper_thigh_circumference'
                ])
        else:
            # При создании нового показываем все поля
            fields.extend([
                'ankle_circumference', 'calf_circumference', 'mid_thigh_circumference',
                'circumference_under_knee', 'Upper_thigh_circumference'
            ])

        return fields


class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 1  # Показывать только 1 пустую строку
    classes = ['collapse']  # Сворачиваем по умолчанию
    fields = ['image', 'image_preview', 'main']  # Показываем превью
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 50px;" />')
        return "Нет изображения"
    image_preview.short_description = 'Превью'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    inlines = [GalleryInline, ]
    list_display = ['name', 'brand', 'price', 'stock', 'available', 'created', 'updated', 'main_image_preview']
    list_filter = ['brand', 'available', 'Class_compress', 'Male', 'created']
    search_fields = ['name', 'brand__name', 'articul', 'code']
    list_editable = ['price', 'stock', 'available']
    readonly_fields = ['created', 'updated', 'main_image_detailed_preview', 'all_images_preview']  # ← Добавил all_images_preview
    date_hierarchy = 'created'

    def main_image_preview(self, obj):
        """Превью главного изображения в списке товаров"""
        main_image = obj.images.filter(main=True).first()
        if not main_image:
            main_image = obj.images.first()  # Если нет главного, берем первое

        if main_image and main_image.image:
            return mark_safe(f'<img src="{main_image.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />')
        return "━"
    main_image_preview.short_description = 'Главное фото'

    def main_image_detailed_preview(self, obj):
        """Детальное превью главного изображения в форме редактирования"""
        main_image = obj.images.filter(main=True).first()
        if not main_image:
            main_image = obj.images.first()

        if main_image and main_image.image:
            return mark_safe(f'''
                <div style="text-align: center;">
                    <img src="{main_image.image.url}" style="max-height: 300px; border-radius: 8px; border: 2px solid #ddd;" />
                    <p style="margin-top: 10px; color: #666;">
                        <strong>Главное изображение:</strong> {main_image.image.name}
                    </p>
                </div>
            ''')
        return mark_safe('<p style="color: #999;">Главное изображение не установлено</p>')
    main_image_detailed_preview.short_description = 'Текущее главное изображение'

    def all_images_preview(self, obj):
        """Превью всех изображений товара"""
        images = obj.images.all()
        if images:
            html = '<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">'
            for gallery_item in images:
                if gallery_item.image:
                    border_style = "3px solid #007bff" if gallery_item.main else "1px solid #ddd"
                    html += f'''
                        <div style="text-align: center;">
                            <img src="{gallery_item.image.url}" style="max-height: 100px; border: {border_style}; border-radius: 4px;" />
                            <div style="font-size: 11px; margin-top: 5px; color: {"#007bff" if gallery_item.main else "#666"}">
                                {"★ ГЛАВНОЕ" if gallery_item.main else "доп."}
                            </div>
                        </div>
                    '''
            html += '</div>'
            return mark_safe(html)
        return "Изображения не загружены"
    all_images_preview.short_description = 'Все изображения товара'

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'name', 'slug', 'brand',
                'price', 'stock', 'available'
            )
        }),

        ('Артикулы и коды', {
            'fields': ('articul', 'code'),
            'classes': ('collapse',)
        }),

        ('Основные характеристики', {
            'fields': (
                'Appointment', 'Male', 'Color',
                'Class_compress', 'Type_product'
            )
        }),

        ('Размеры и модели', {
            'fields': (
                'Size', 'Model_type', 'Wide_hips', 'Side'
            ),
            'classes': ('collapse',)
        }),

        ('Дополнительные характеристики', {
            'fields': ('Sock',),
            'classes': ('collapse',)
        }),

        ('Изображения', {
            'fields': ('main_image_detailed_preview', 'all_images_preview'),
            'classes': ('wide',)
        }),

        ('SEO оптимизация', {
            'fields': (
                'seo_title',
                'seo_description',
                'seo_alt',
                'seo_h1',
                'seo_keywords'
            ),
            'classes': ('collapse',)
        }),

        ('Даты', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )
