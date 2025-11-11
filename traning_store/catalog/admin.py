from django.contrib import admin

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
    list_display = ['name']


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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}
    inlines = [GalleryInline, ]
