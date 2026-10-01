from .utils import get_cart_from_request

def cart_total(request):
    """Context processor to add cart to all templates"""
    cart = get_cart_from_request(request)
    return {
        'cart_total_items': cart.total_items if cart else 0,
        'cart_subtotal': cart.subtotal if cart else 0,
        'cart_total': cart.total if cart else 0,
        'cart': cart,
    }
