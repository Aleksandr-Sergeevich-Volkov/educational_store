from django.contrib import admin


from .models import (Country,Brend,Appointment,Male,Color,
                     Class_compress,Soсk,Type_product,Wide_hips,Side,
                     Size,Model_type,Product)

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
#admin.site.register(Product)

@admin.register(Product)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'image_tag']

    def image_tag(self, obj):
        return obj.image.url if obj.image else None
    image_tag.short_description = 'Image'