from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['subtotal', 'total_price']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'status', 'total_items', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'session_key']
    inlines = [CartItemInline]
    readonly_fields = ['total_items', 'subtotal', 'total_discount', 'total']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'variant', 'quantity', 'price', 'subtotal']
    list_filter = ['created_at']
    search_fields = ['variant__sku', 'variant__product__name']