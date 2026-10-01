from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Wishlist, WishlistItem
from catalog.models import Product

@login_required
def wishlist_detail(request):
    """View user's wishlist"""
    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user, is_default=True,
        defaults={'name': 'My Wishlist'}
    )
    items = wishlist.items.select_related('product')
    
    context = {
        'wishlist': wishlist,
        'items': items,
    }
    return render(request, 'wishlist/wishlist_detail.html', context)

@login_required
@require_POST
def wishlist_add(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user, is_default=True
    )
    
    item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist, product=product
    )
    
    if created:
        return JsonResponse({'success': True, 'message': 'Added to wishlist', 'in_wishlist': True})
    return JsonResponse({'success': True, 'message': 'Already in wishlist', 'in_wishlist': True})

@login_required
@require_POST
def wishlist_remove(request, product_id):
    """Remove product from wishlist"""
    WishlistItem.objects.filter(
        wishlist__user=request.user, product_id=product_id
    ).delete()
    
    if request.headers.get('HX-Request'):
        wishlist = Wishlist.objects.get(user=request.user, is_default=True)
        items = wishlist.items.select_related('product')
        return render(request, 'wishlist/partials/wishlist_items.html', {
            'wishlist': wishlist, 'items': items
        })
    
    return JsonResponse({'success': True, 'message': 'Removed from wishlist', 'in_wishlist': False})

@login_required
def wishlist_toggle(request, product_id):
    """Toggle wishlist status"""
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user, is_default=True)
    
    item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
    
    if item:
        item.delete()
        return JsonResponse({'success': True, 'in_wishlist': False, 'message': 'Removed from wishlist'})
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        return JsonResponse({'success': True, 'in_wishlist': True, 'message': 'Added to wishlist'})