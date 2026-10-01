from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, ProductVariant

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'order', 'product_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'order']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'product_count']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['sku', 'color', 'color_code', 'size', 'price', 'compare_at_price', 'quantity', 'is_active']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock_status', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'is_new', 'is_best_seller', 'category', 'gender']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured', 'price']
    inlines = [ProductVariantInline]
    readonly_fields = ['average_rating', 'total_reviews', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'category', 'brand', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_at_price', 'cost_per_item')
        }),
        ('Attributes', {
            'fields': ('gender', 'material', 'care_instructions', 'fit', 'tags')
        }),
        ('Media', {
            'fields': ('main_image', 'gallery_images', 'video_url')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'is_new', 'is_best_seller', 'is_trending', 'is_on_sale')
        }),
        ('Ratings', {
            'fields': ('average_rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status(self, obj):
        total = sum(v.available_quantity for v in obj.variants.filter(is_active=True))
        if total == 0:
            return format_html('<span style="color: red;">{}</span>', 'Out of Stock')
        elif total < 10:
            return format_html('<span style="color: orange;">Low: {}</span>', total)
        return format_html('<span style="color: green;">In Stock: {}</span>', total)
    stock_status.short_description = 'Stock'

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['sku', 'product', 'color', 'size', 'quantity', 'reserved_quantity', 'available_quantity', 'is_active']
    list_filter = ['is_active', 'color', 'size']
    search_fields = ['sku', 'product__name']
    list_editable = ['quantity', 'is_active']