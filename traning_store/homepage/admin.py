from django.contrib import admin

from .models import City, Comment, Post

admin.site.register(Post)
admin.site.register(Comment)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ru', 'region', 'country', 'detection_count', 'is_active', 'is_popular')
    list_filter = ('is_active', 'is_popular', 'is_default', 'country', 'region')
    search_fields = ('name', 'name_ru', 'region')
    list_editable = ('name_ru', 'is_active', 'is_popular')
    ordering = ('-detection_count', 'name')
    actions = ['mark_as_popular', 'fix_russian_names']

    def mark_as_popular(self, request, queryset):
        updated = queryset.update(is_popular=True)
        self.message_user(request, f'{updated} городов отмечены как популярные')
    mark_as_popular.short_description = "Отметить как популярные"

    def fix_russian_names(self, request, queryset):
        """Полуавтоматическое исправление - показывает подсказки"""
        for city in queryset:
            if city.name_ru and any(c.isalpha() and ord(c) < 128 for c in city.name_ru):
                self.message_user(
                    request,
                    f'Город {city.name} ({city.name_ru}) - нужно ввести русское название'
                )
    fix_russian_names.short_description = "Проверить русские названия"
