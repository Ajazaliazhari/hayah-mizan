from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel
from catalog.models import Product

User = get_user_model()

class Wishlist(BaseModel):
    """User wishlist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    name = models.CharField(max_length=100, default='My Wishlist')
    is_default = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"
    
    @property
    def item_count(self):
        return self.items.count()

class WishlistItem(BaseModel):
    """Items in wishlist"""
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    
    class Meta:
        unique_together = ['wishlist', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} in {self.wishlist.name}"