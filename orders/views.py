from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import Order, OrderItem, OrderEvent, ReturnRequest
from cart.utils import get_cart_from_request, clear_cart
from core.models import Address

@login_required
def checkout(request):
    """Checkout page - renders UI for Razorpay"""
    cart = get_cart_from_request(request)
    
    if not cart or cart.total_items == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:detail')
    
    cart_items = cart.items.select_related('variant', 'variant__product')
    addresses = request.user.addresses.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'addresses': addresses,
        'default_address': addresses.filter(is_default=True).first(),
        'razorpay_key_id': 'YOUR_RAZORPAY_KEY_ID',  # UI only placeholder
    }
    return render(request, 'orders/checkout.html', context)

@login_required
@require_POST
def place_order(request):
    """Place order after payment (backend placeholder - UI only flow)"""
    cart = get_cart_from_request(request)
    
    if not cart or cart.total_items == 0:
        return JsonResponse({'success': False, 'error': 'Cart is empty'}, status=400)
    
    try:
        with transaction.atomic():
            # Determine shipping address
            address_id = request.POST.get('address_id')
            if address_id:
                address = get_object_or_404(Address, id=address_id, user=request.user)
            else:
                address = None
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                customer_name=request.user.get_full_name(),
                customer_email=request.user.email,
                customer_phone=request.user.phone or 'N/A',
                shipping_name=address.full_name if address else request.POST.get('full_name'),
                shipping_phone=address.phone if address else request.POST.get('phone'),
                shipping_address_line1=address.address_line1 if address else request.POST.get('address_line1'),
                shipping_address_line2=address.address_line2 if address else request.POST.get('address_line2', ''),
                shipping_city=address.city if address else request.POST.get('city'),
                shipping_state=address.state if address else request.POST.get('state'),
                shipping_pincode=address.pincode if address else request.POST.get('pincode'),
                subtotal=cart.subtotal,
                discount_amount=cart.total_discount,
                shipping_amount=0,
                tax_amount=0,
                total_amount=cart.total,
                payment_method=request.POST.get('payment_method', 'razorpay'),
                payment_status='pending',  # UI only - backend would verify
                status='pending',
            )
            
            # Create order items
            for cart_item in cart.items.select_related('variant', 'variant__product'):
                variant = cart_item.variant
                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    product_name=variant.product.name,
                    product_sku=variant.sku,
                    color=variant.color,
                    size=variant.size,
                    product_image=variant.image.url if variant.image else variant.product.main_image.url,
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                    compare_at_price=cart_item.compare_at_price,
                    discount_amount=cart_item.discount_amount,
                    total_price=cart_item.total_price,
                )
            
            # Create initial order event
            OrderEvent.objects.create(
                order=order,
                status='pending',
                description='Order placed successfully',
                created_by=request.user,
            )
            
            # Clear cart
            clear_cart(request)
            
            return JsonResponse({
                'success': True,
                'order_number': order.order_number,
                'redirect_url': f'/orders/{order.order_number}/confirmation/'
            })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def order_confirmation(request, order_number):
    """Order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/confirmation.html', {'order': order})

@login_required
def order_detail(request, order_number):
    """Order detail page"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def order_list(request):
    """List user's orders"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
@require_POST
def cancel_order(request, order_number):
    """Cancel an order"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if not order.is_cancellable:
        return JsonResponse({'success': False, 'error': 'Order cannot be cancelled'}, status=400)
    
    with transaction.atomic():
        order.status = 'cancelled'
        order.save()
        OrderEvent.objects.create(
            order=order,
            status='cancelled',
            description='Order cancelled by customer',
            created_by=request.user,
        )
    
    return JsonResponse({'success': True, 'message': 'Order cancelled successfully'})

@login_required
def request_return(request, order_number):
    """Request return/exchange"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if not order.is_returnable:
        messages.error(request, 'This order is not eligible for return.')
        return redirect('orders:detail', order_number=order_number)
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        return_type = request.POST.get('return_type', 'return')
        reason = request.POST.get('reason', '')
        
        order_item = get_object_or_404(OrderItem, id=item_id, order=order)
        
        ReturnRequest.objects.create(
            order=order, order_item=order_item, user=request.user,
            return_type=return_type, reason=reason,
        )
        messages.success(request, 'Return request submitted successfully.')
        return redirect('orders:detail', order_number=order_number)
    
    return render(request, 'orders/return_request.html', {'order': order})