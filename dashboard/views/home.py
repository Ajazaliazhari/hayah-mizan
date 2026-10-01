from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from catalog.models import Product, Category, Brand
from accounts.models import User
from reviews.models import Review
from dashboard.decorators import staff_required


@staff_required
def dashboard_home(request):
    """Dashboard home with stats"""
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    last_7_days = now - timedelta(days=7)

    # Revenue & orders
    total_revenue = Order.objects.filter(
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    revenue_30d = Order.objects.filter(
        payment_status='paid', created_at__gte=last_30_days
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    revenue_7d = Order.objects.filter(
        payment_status='paid', created_at__gte=last_7_days
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status__in=['pending', 'payment_confirmed', 'processing']).count()

    # Customers
    total_customers = User.objects.filter(is_staff=False).count()
    new_customers_30d = User.objects.filter(
        is_staff=False, date_joined__gte=last_30_days
    ).count()

    # Products
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    total_brands = Brand.objects.filter(is_active=True).count()
    out_of_stock = Product.objects.filter(is_active=True, variants__quantity=0).distinct().count()

    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:8]

    # Pending reviews
    pending_reviews = Review.objects.filter(is_approved=False).count()

    # Top products
    top_products = Product.objects.filter(
        is_active=True
    ).order_by('-total_reviews', '-average_rating')[:5]

    # Average order value
    aov = Order.objects.filter(payment_status='paid').aggregate(avg=Avg('total_amount'))['avg'] or 0

    context = {
        'total_revenue': total_revenue,
        'revenue_30d': revenue_30d,
        'revenue_7d': revenue_7d,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_customers': total_customers,
        'new_customers_30d': new_customers_30d,
        'total_products': total_products,
        'total_categories': total_categories,
        'total_brands': total_brands,
        'out_of_stock': out_of_stock,
        'recent_orders': recent_orders,
        'pending_reviews': pending_reviews,
        'top_products': top_products,
        'avg_order_value': aov,
        'active_page': 'home',
    }
    return render(request, 'dashboard/home.html', context)
