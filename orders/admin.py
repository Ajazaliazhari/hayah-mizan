from django.contrib import admin
from .models import Order, OrderItem, OrderEvent, ReturnRequest

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'color', 'size', 'quantity', 'price', 'total_price']

class OrderEventInline(admin.TabularInline):
    model = OrderEvent
    extra = 0
    readonly_fields = ['status', 'description', 'created_by', 'created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'total_amount', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_email', 'customer_name', 'customer_phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderEventInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'payment_method')
        }),
        ('Customer', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipping Address', {
            'fields': ('shipping_name', 'shipping_phone', 'shipping_address_line1',
                      'shipping_address_line2', 'shipping_landmark', 'shipping_city',
                      'shipping_state', 'shipping_pincode', 'shipping_country')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'discount_amount', 'coupon_code',
                      'shipping_amount', 'tax_amount', 'total_amount')
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'carrier', 'shipped_at', 'delivered_at')
        }),
        ('Payment', {
            'fields': ('payment_id', 'payment_signature')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
    )

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'return_type', 'status', 'created_at']
    list_filter = ['return_type', 'status']
    search_fields = ['order__order_number']