from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel
from catalog.models import Product

User = get_user_model()

class Review(BaseModel):
    """Product reviews"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    
    # Review images
    images = models.JSONField(default=list, blank=True)
    
    # Moderation
    is_approved = models.BooleanField(default=False)
    is_verified_purchase = models.BooleanField(default=False)
    
    # Helpfulness
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating}★)"
    
    def save(self, *args, **kwargs):
        # Check if verified purchase
        if self.order:
            self.is_verified_purchase = self.order.items.filter(
                variant__product=self.product
            ).exists()
        super().save(*args, **kwargs)
        
        # Update product rating
        self.product.average_rating = self.product.reviews.filter(
            is_approved=True
        ).aggregate(models.Avg('rating'))['rating__avg'] or 0
        self.product.total_reviews = self.product.reviews.filter(is_approved=True).count()
        self.product.save()