from django.contrib import admin

from .models import (Appointment, Brend, Class_compress, Color, Country,
                     Gallery, Male, Model_type, Product, Side, Size, Soсk,
                     Type_product, Wide_hips)

admin.site.register(Country)
admin.site.register(Brend)
admin.site.register(Appointment)
admin.site.register(Male)
admin.site.register(Color)
admin.site.register(Class_compress)
admin.site.register(Soсk)
admin.site.register(Type_product)
admin.site.register(Wide_hips)
admin.site.register(Side)
admin.site.register(Size)
admin.site.register(Model_type)
admin.site.register(Gallery)


class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}
    inlines = [GalleryInline,]
