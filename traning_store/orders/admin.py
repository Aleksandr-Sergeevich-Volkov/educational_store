import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product', 'size']


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; '
    'filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields()
              if not field.many_to_many and not field.one_to_many]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = 'Export to CSV'


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'first_name', 'last_name', 'email',
        'address', 'address_pvz', 'postal_code', 'city',
        'paid', 'created', 'updated',
        'track_number',  # Добавили трек-номер
        'order_id',       # Добавили ID заказа в CDEK
        'get_status'      # Кастомное поле для статуса
    ]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    actions = [export_to_csv]

    def get_status(self, obj):
        """Отображение статуса CDEK в админке"""
        if obj.track_number:
            # Здесь можно добавить вызов API для получения актуального статуса
            # Или просто показать сохраненный статус
            return obj.delivery_status or "Статус неизвестен"
        return "Нет трек-номера"
    get_status.short_description = "Статус доставки "


admin.site.register(Order, OrderAdmin)
