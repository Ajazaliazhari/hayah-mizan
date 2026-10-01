from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Coupon
from cart.utils import get_cart_from_request

@require_POST
def apply_coupon(request):
    """Apply coupon code"""
    code = request.POST.get('code', '').upper().strip()
    cart = get_cart_from_request(request)
    
    if not cart or cart.total_items == 0:
        return JsonResponse({'success': False, 'error': 'Cart is empty'}, status=400)
    
    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invalid coupon code'}, status=404)
    
    if not coupon.is_valid:
        return JsonResponse({'success': False, 'error': 'Coupon is expired or invalid'}, status=400)
    
    # Check per-user limit
    if request.user.is_authenticated:
        usage_count = coupon.usages.filter(user=request.user).count()
        if usage_count >= coupon.usage_limit_per_user:
            return JsonResponse({'success': False, 'error': 'You have reached the usage limit for this coupon'}, status=400)
    
    discount = coupon.calculate_discount(cart.subtotal)
    if discount <= 0:
        return JsonResponse({
            'success': False,
            'error': f'Minimum cart value of ₹{coupon.min_cart_value} required'
        }, status=400)
    
    request.session['coupon_code'] = coupon.code
    request.session['coupon_discount'] = str(discount)
    
    return JsonResponse({
        'success': True,
        'message': f'Coupon applied! You saved ₹{discount}',
        'discount': str(discount),
        'new_total': str(cart.subtotal - discount),
    })

@require_POST
def remove_coupon(request):
    """Remove applied coupon"""
    request.session.pop('coupon_code', None)
    request.session.pop('coupon_discount', None)
    return JsonResponse({'success': True, 'message': 'Coupon removed'})