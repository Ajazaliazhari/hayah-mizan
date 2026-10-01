from django.utils import timezone
from .models import Cart, CartItem
from catalog.models import ProductVariant

def get_cart_from_request(request):
    """Get or create cart for user/session"""
    cart = None
    cart_id = request.session.get('cart_id')
    
    # Try to get cart by ID
    if cart_id:
        try:
            cart = Cart.objects.get(id=cart_id, status='active')
            # Check if cart hasn't expired
            if cart.expires_at and cart.expires_at < timezone.now():
                cart.status = 'expired'
                cart.save()
                cart = None
        except Cart.DoesNotExist:
            cart = None
    
    # If user is authenticated and no cart found
    if request.user.is_authenticated:
        if cart:
            # Assign cart to user if it was guest
            if not cart.user:
                cart.user = request.user
                cart.save()
        else:
            # Try to get active cart for user
            cart = Cart.objects.filter(user=request.user, status='active').first()
            if cart:
                request.session['cart_id'] = cart.id
            else:
                cart = create_cart(request)
    elif not cart:
        # Create guest cart
        cart = create_cart(request)
    
    return cart

def create_cart(request):
    """Create a new cart"""
    cart = Cart.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key if not request.user.is_authenticated else None,
        status='active',
        expires_at=timezone.now() + timezone.timedelta(days=30)  # 30 days expiry
    )
    request.session['cart_id'] = cart.id
    return cart

def add_to_cart(request, variant_id, quantity=1):
    """Add item to cart"""
    cart = get_cart_from_request(request)
    
    try:
        variant = ProductVariant.objects.get(id=variant_id, is_active=True)
        if variant.available_quantity < quantity:
            raise ValueError("Insufficient stock")
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={
                'quantity': quantity,
                'price': variant.effective_price,
                'compare_at_price': variant.effective_compare_at_price,
            }
        )
        
        if not created:
            # Update quantity
            if cart_item.quantity + quantity > variant.available_quantity:
                raise ValueError("Insufficient stock")
            cart_item.quantity += quantity
            cart_item.save()
        
        # Update cart totals
        cart.update_totals()
        
        return cart_item
    
    except ProductVariant.DoesNotExist:
        raise ValueError("Product variant not found")
    except Exception as e:
        raise e

def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart = get_cart_from_request(request)
    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart_item.delete()
        cart.update_totals()
        return True
    except CartItem.DoesNotExist:
        return False

def update_cart_quantity(request, item_id, quantity):
    """Update cart item quantity"""
    cart = get_cart_from_request(request)
    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        if quantity <= 0:
            cart_item.delete()
        else:
            if quantity > cart_item.variant.available_quantity:
                raise ValueError("Insufficient stock")
            cart_item.quantity = quantity
            cart_item.save()
        cart.update_totals()
        return True
    except CartItem.DoesNotExist:
        return False

def clear_cart(request):
    """Clear all items from cart"""
    cart = get_cart_from_request(request)
    cart.items.all().delete()
    cart.update_totals()
    return True

def get_cart_totals(request):
    """Get cart totals for display"""
    cart = get_cart_from_request(request)
    return {
        'total_items': cart.total_items if cart else 0,
        'subtotal': cart.subtotal if cart else 0,
        'discount': cart.total_discount if cart else 0,
        'total': cart.total if cart else 0,
    }
