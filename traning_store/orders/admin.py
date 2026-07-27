import csv
import datetime
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product", "size", "color", "m_type"]
    readonly_fields = ["get_cost_display"]
    fields = [
        "product",
        "size",
        "color",
        "m_type",
        "price",
        "quantity",
        "get_cost_display",
    ]
    extra = 0

    def get_cost_display(self, obj):
        if obj.price and obj.quantity:
            return f"{obj.get_cost():.2f} руб."
        return "0.00 руб."

    get_cost_display.short_description = "Сумма"


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={opts.verbose_name}.csv"
    writer = csv.writer(response)

    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
    writer.writerow([field.verbose_name for field in fields])

    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")
            elif isinstance(value, bool):
                value = "Да" if value else "Нет"
            elif isinstance(value, Decimal):
                value = f"{value:.2f}"
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = "Экспорт в CSV"


def print_torg12_action(modeladmin, request, queryset):
    """
    Экшен для печати ТОРГ-12 - ПРЯМОЙ РЕНДЕР без редиректа
    """
    if queryset.count() != 1:
        modeladmin.message_user(
            request, "Пожалуйста, выберите ОДИН заказ для печати", level="error"
        )
        return

    order = queryset.first()
    context = {"order": order, "usn": True, "vat_text": "Без НДС (УСН)"}

    # Прямой рендер шаблона - без редиректа!
    return render(request, "admin/order_torg12.html", context)


print_torg12_action.short_description = "Печать ТОРГ-12"


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "get_full_name",
        "email",
        "get_delivery_address_short",
        "get_total_cost_display",
        "paid",
        "created",
        "delivery_type",
        "track_number",
        "get_status",
    ]
    list_filter = ["paid", "created", "updated", "delivery_type"]
    search_fields = ["id", "first_name", "last_name", "email", "track_number"]
    inlines = [OrderItemInline]
    actions = [export_to_csv, print_torg12_action]  # Только прямой рендер
    readonly_fields = [
        "created",
        "updated",
        "last_status_update",
        "get_total_cost_display",
    ]

    fieldsets = (
        (
            "Информация о покупателе",
            {
                "fields": (
                    ("first_name", "last_name"),
                    ("email"),
                    "address",
                    "address_pvz",
                    ("postal_code", "city"),
                )
            },
        ),
        (
            "Финансы",
            {
                "fields": (
                    "paid",
                    "get_total_cost_display",
                    ("coupon", "discount"),
                    "delivery_sum",
                )
            },
        ),
        (
            "Доставка (для курьера)",
            {
                "fields": (
                    ("delivery_type", "track_number"),
                    ("order_id", "delivery_status"),
                ),
                "description": "Информация для курьерской службы",
            },
        ),
        (
            "Системные данные",
            {
                "fields": ("created", "updated", "last_status_update"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()

    get_full_name.short_description = "Покупатель"
    get_full_name.admin_order_field = "last_name"

    def get_delivery_address_short(self, obj):
        addr = obj.get_delivery_address()
        if len(addr) > 30:
            return addr[:30] + "..."
        return addr

    get_delivery_address_short.short_description = "Адрес доставки"

    def get_status(self, obj):
        if obj.track_number:
            return obj.delivery_status or "В пути"
        return "Нет трек-номера"

    get_status.short_description = "Статус доставки"

    def get_total_cost_display(self, obj):
        return f"{obj.get_total_cost():.2f} руб."

    get_total_cost_display.short_description = "Итого с доставкой"


admin.site.register(Order, OrderAdmin)


# Отменяем стандартную регистрацию
admin.site.unregister(User)


class MyUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "date_joined",
        "first_name",
        "last_name",
        "is_staff",
    )


admin.site.register(User, MyUserAdmin)
