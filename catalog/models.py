from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from core.models import BaseModel

class Category(BaseModel):
    """Product categories"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font awesome icon class")
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})
    
    @property
    def is_parent(self):
        return not self.parent

class Brand(BaseModel):
    """Product brands"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(BaseModel):
    """Main product model"""
    
    GENDER_CHOICES = (
        ('M', 'Men'),
        ('F', 'Women'),
        ('K', 'Kids'),
        ('U', 'Unisex'),
    )
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    
    # Relationships
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Original/MRP price")
    cost_per_item = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Attributes
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    material = models.CharField(max_length=100, blank=True)
    care_instructions = models.TextField(blank=True)
    fit = models.CharField(max_length=50, blank=True)
    
    # Media
    main_image = models.ImageField(upload_to='products/')
    gallery_images = models.JSONField(default=list, blank=True)  # List of image URLs
    video_url = models.URLField(blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    
    # Ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    
    # Tags for search
    tags = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.meta_title:
            self.meta_title = self.name
        # Check if on sale
        if self.compare_at_price and self.compare_at_price > self.price:
            self.is_on_sale = True
        else:
            self.is_on_sale = False
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})
    
    @property
    def discount_percentage(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0
    
    @property
    def gallery_images_list(self):
        return self.gallery_images or []
    
    @property
    def variants_with_stock(self):
        return self.variants.filter(is_active=True)

    @property
    def has_main_image(self):
        """Check if main image file actually exists"""
        return bool(self.main_image and self.main_image.name)

    @property
    def main_image_url(self):
        """Safe main image URL with fallback placeholder"""
        if self.main_image and self.main_image.name:
            try:
                return self.main_image.url
            except ValueError:
                pass
        return '/static/images/placeholder.svg'

class ProductVariant(BaseModel):
    """Product variants (size, color combinations)"""
    @property
    def has_image(self):
        """Check if variant image file actually exists"""
        return bool(self.image and self.image.name)

    @property
    def image_url(self):
        """Safe variant image URL with fallback"""
        if self.image and self.image.name:
            try:
                return self.image.url
            except ValueError:
                pass
        # Fallback to product's main image
        if self.product.main_image and self.product.main_image.name:
            try:
                return self.product.main_image.url
            except ValueError:
                pass
        return '/static/images/placeholder.svg'
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=50, unique=True)
    
    # Variant attributes
    color = models.CharField(max_length=50)
    color_code = models.CharField(max_length=7, blank=True, help_text="Hex color code")
    size = models.CharField(max_length=20)
    
    # Pricing override (if different from product)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Stock
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)  # For orders in progress
    low_stock_threshold = models.IntegerField(default=5)
    
    # Images (overrides product images)
    image = models.ImageField(upload_to='variants/', null=True, blank=True)
    
    # Additional attributes
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['color', 'size']
        unique_together = ['product', 'color', 'size']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['product', 'color', 'size']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.color} / {self.size}"
    
    @property
    def available_quantity(self):
        """Get available quantity (total - reserved)"""
        return self.quantity - self.reserved_quantity
    
    @property
    def is_in_stock(self):
        return self.available_quantity > 0
    
    @property
    def is_low_stock(self):
        return 0 < self.available_quantity <= self.low_stock_threshold
    
    @property
    def effective_price(self):
        """Get effective price (variant price if set, otherwise product price)"""
        return self.price if self.price is not None else self.product.price
    
    @property
    def effective_compare_at_price(self):
        """Get effective compare price"""
        return self.compare_at_price if self.compare_at_price is not None else self.product.compare_at_price
    
    def reduce_quantity(self, quantity):
        """Reduce quantity for order"""
        if self.available_quantity < quantity:
            raise ValueError("Insufficient stock")
        self.quantity -= quantity
        self.save()
        return self.quantity
    
    def reserve_quantity(self, quantity):
        """Reserve quantity for order"""
        if self.available_quantity < quantity:
            raise ValueError("Insufficient stock")
        self.reserved_quantity += quantity
        self.save()
        return self.reserved_quantity
    
    def release_reserved_quantity(self, quantity):
        """Release reserved quantity"""
        if self.reserved_quantity < quantity:
            raise ValueError("Invalid reservation release")
        self.reserved_quantity -= quantity
        self.save()
        return self.reserved_quantity
