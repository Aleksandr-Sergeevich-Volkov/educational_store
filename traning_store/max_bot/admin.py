# max_bot/admin.py
from django.contrib import admin

from .models import CartItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'product', 'quantity', 'size', 'color', 'price_at_add', 'created_at')
    list_filter = ('created_at', 'size', 'color')
    search_fields = ('user_id', 'product__name')
    readonly_fields = ('created_at', 'updated_at')
