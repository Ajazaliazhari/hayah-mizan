from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from .utils import (get_cart_from_request, add_to_cart, remove_from_cart,
                    update_cart_quantity, clear_cart, get_cart_totals)

def cart_detail(request):
    """View cart"""
    cart = get_cart_from_request(request)
    cart_items = cart.items.select_related('variant', 'variant__product') if cart else []
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart_detail.html', context)

@require_POST
def cart_add(request):
    """Add item to cart - AJAX"""
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        cart_item = add_to_cart(request, variant_id, quantity)
        cart = get_cart_from_request(request)
        
        if request.headers.get('HX-Request'):
            return render(request, 'cart/partials/cart_sidebar.html', {'cart': cart})
        
        return JsonResponse({
            'success': True,
            'message': 'Item added to cart',
            'cart_total_items': cart.total_items,
            'cart_total': str(cart.total),
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_POST
def cart_update(request, item_id):
    """Update cart item quantity"""
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        update_cart_quantity(request, item_id, quantity)
        cart = get_cart_from_request(request)
        
        if request.headers.get('HX-Request'):
            cart_items = cart.items.select_related('variant', 'variant__product')
            return render(request, 'cart/partials/cart_items.html', {
                'cart': cart, 'cart_items': cart_items
            })
        
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
            'cart_total': str(cart.total),
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_POST
def cart_remove(request, item_id):
    """Remove item from cart"""
    remove_from_cart(request, item_id)
    cart = get_cart_from_request(request)
    
    if request.headers.get('HX-Request'):
        cart_items = cart.items.select_related('variant', 'variant__product')
        return render(request, 'cart/partials/cart_items.html', {
            'cart': cart, 'cart_items': cart_items
        })
    
    return JsonResponse({
        'success': True,
        'cart_total_items': cart.total_items,
        'cart_total': str(cart.total),
    })

@require_POST
def cart_clear(request):
    """Clear entire cart"""
    clear_cart(request)
    return JsonResponse({'success': True, 'cart_total_items': 0, 'cart_total': '0.00'})

def cart_sidebar(request):
    """Cart sidebar for HTMX"""
    cart = get_cart_from_request(request)
    return render(request, 'cart/partials/cart_sidebar.html', {'cart': cart})