from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (Appointment, Brend, Class_compress, Color, Country,
                     Gallery, Male, Model_type, Product, Side, Size,
                     SizeDetail, Soсk, Type_product, Wide_hips)

admin.site.register(Country)
# admin.site.register(Brend)
admin.site.register(Appointment)
admin.site.register(Male)
admin.site.register(Color)
admin.site.register(Class_compress)
admin.site.register(Soсk)
admin.site.register(Type_product)
admin.site.register(Wide_hips)
admin.site.register(Side)
# admin.site.register(Size)
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
    fields = ['image', 'image_preview']  # Показываем превью
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 50px;" />')
        return "Нет изображения"
    image_preview.short_description = 'Превью'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}
    inlines = [GalleryInline, ]
