import uuid
from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel, Address
from catalog.models import ProductVariant

User = get_user_model()

class Order(BaseModel):
    """Order model"""
    
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('payment_confirmed', 'Payment Confirmed'),
        ('processing', 'Processing'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    )
    
    PAYMENT_METHODS = (
        ('razorpay', 'Razorpay'),
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    )
    
    # Order identification
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    
    # Customer info
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    
    # Shipping address
    shipping_name = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=15)
    shipping_address_line1 = models.CharField(max_length=200)
    shipping_address_line2 = models.CharField(max_length=200, blank=True)
    shipping_landmark = models.CharField(max_length=100, blank=True)
    shipping_city = models.CharField(max_length=50)
    shipping_state = models.CharField(max_length=50)
    shipping_pincode = models.CharField(max_length=10)
    shipping_country = models.CharField(max_length=50, default='India')
    
    # Billing address (optional, same as shipping by default)
    billing_same_as_shipping = models.BooleanField(default=True)
    billing_name = models.CharField(max_length=100, blank=True)
    billing_address_line1 = models.CharField(max_length=200, blank=True)
    billing_address_line2 = models.CharField(max_length=200, blank=True)
    billing_city = models.CharField(max_length=50, blank=True)
    billing_state = models.CharField(max_length=50, blank=True)
    billing_pincode = models.CharField(max_length=10, blank=True)
    billing_country = models.CharField(max_length=50, default='India')
    
    # Order details
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='razorpay')
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=50, blank=True)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Payment details
    payment_id = models.CharField(max_length=100, blank=True)
    payment_signature = models.CharField(max_length=200, blank=True)
    
    # Shipping/Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=100, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Invoice
    invoice_number = models.CharField(max_length=50, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            import string
            self.order_number = 'HM' + ''.join(random.choices(string.digits, k=10))
        if self.billing_same_as_shipping:
            self.billing_name = self.shipping_name
            self.billing_address_line1 = self.shipping_address_line1
            self.billing_address_line2 = self.shipping_address_line2
            self.billing_city = self.shipping_city
            self.billing_state = self.shipping_state
            self.billing_pincode = self.shipping_pincode
            self.billing_country = self.shipping_country
        super().save(*args, **kwargs)
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def is_cancellable(self):
        return self.status in ['pending', 'payment_confirmed', 'processing']
    
    @property
    def is_returnable(self):
        if self.status != 'delivered':
            return False
        from django.utils import timezone
        from datetime import timedelta
        return self.delivered_at and (timezone.now() - self.delivered_at) <= timedelta(days=7)
    
    @property
    def shipping_address_display(self):
        parts = [self.shipping_address_line1]
        if self.shipping_address_line2:
            parts.append(self.shipping_address_line2)
        if self.shipping_landmark:
            parts.append(f"Near {self.shipping_landmark}")
        parts.append(f"{self.shipping_city}, {self.shipping_state} - {self.shipping_pincode}")
        parts.append(self.shipping_country)
        return ', '.join(parts)

class OrderItem(BaseModel):
    """Individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    
    # Snapshot of product details at time of order
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    product_image = models.URLField(blank=True)
    
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    @property
    def item_subtotal(self):
        return self.price * self.quantity

class OrderEvent(BaseModel):
    """Track order status changes"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='events')
    status = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"

class ReturnRequest(BaseModel):
    """Return/Exchange requests"""
    
    RETURN_TYPES = (
        ('return', 'Return'),
        ('exchange', 'Exchange'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_requests')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='return_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='return_requests')
    
    return_type = models.CharField(max_length=20, choices=RETURN_TYPES, default='return')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refund_status = models.CharField(max_length=20, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.return_type} for {self.order.order_number}"