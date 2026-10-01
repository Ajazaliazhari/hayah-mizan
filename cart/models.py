from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel
from catalog.models import ProductVariant

User = get_user_model()

class Cart(BaseModel):
    """Shopping cart model"""
    
    CART_STATUS = (
        ('active', 'Active'),
        ('abandoned', 'Abandoned'),
        ('converted', 'Converted to Order'),
        ('expired', 'Expired'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    status = models.CharField(max_length=20, choices=CART_STATUS, default='active')
    total_items = models.IntegerField(default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Timestamps
    last_modified = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['session_key', 'status']),
        ]
    
    def __str__(self):
        return f"Cart #{self.id} - {self.user or self.session_key}"
    
    def update_totals(self):
        """Update cart totals"""
        items = self.items.all()
        self.total_items = items.count()
        self.subtotal = sum(item.subtotal for item in items)
        self.total_discount = sum(item.discount_amount for item in items)
        self.total = self.subtotal - self.total_discount
        self.save()
        return self.total
    
    def get_cart_items(self):
        """Get all cart items with variant details"""
        return self.items.select_related('variant', 'variant__product')

class CartItem(BaseModel):
    """Individual cart item"""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['cart', 'variant']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.variant.product.name} x {self.quantity}"
    
    @property
    def subtotal(self):
        """Calculate item subtotal"""
        if self.price is None or self.quantity is None:
            return 0
        return self.price * self.quantity
    
    @property
    def total_discount(self):
        """Calculate total discount for this item"""
        if self.discount_amount is None or self.quantity is None:
            return 0
        return self.discount_amount * self.quantity
    
    @property
    def final_price(self):
        """Final price after discount"""
        if self.price is None:
            return 0
        discount = self.discount_amount or 0
        return self.price - discount
    
    @property
    def total_price(self):
        """Total price for this item (after discount)"""
        if self.price is None or self.quantity is None:
            return 0
        return self.final_price * self.quantity