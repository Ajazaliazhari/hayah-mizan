# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.views.generic import TemplateView, ListView
# from catalog.models import Product, Category, Brand
# from .models import ContactMessage


from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView, ListView
from django.db import models          # ← ADD THIS LINE
from django.db.models import Q, Min, Max   # optional but useful
from catalog.models import Product, Category, Brand
from .models import ContactMessage


def home(request):
    """Homepage view"""
    context = {
        'featured_products': Product.objects.filter(is_featured=True, is_active=True)[:8],
        'new_arrivals': Product.objects.filter(is_new=True, is_active=True)[:8],
        'best_sellers': Product.objects.filter(is_best_seller=True, is_active=True)[:8],
        'trending_products': Product.objects.filter(is_trending=True, is_active=True)[:8],
        'categories': Category.objects.filter(is_active=True, parent=None)[:6],
        'brands': Brand.objects.filter(is_active=True)[:8],
    }
    return render(request, 'core/home.html', context)

def about(request):
    """About page"""
    return render(request, 'core/about.html')

def contact(request):
    """Contact page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name, email=email, phone=phone,
            subject=subject, message=message
        )
        messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
        return redirect('core:contact')
    
    return render(request, 'core/contact.html')

def faq(request):
    """FAQ page"""
    return render(request, 'core/faq.html')

def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'core/privacy.html')

def terms_conditions(request):
    """Terms and conditions page"""
    return render(request, 'core/terms.html')

def shipping_policy(request):
    """Shipping policy page"""
    return render(request, 'core/shipping.html')

def return_policy(request):
    """Return policy page"""
    return render(request, 'core/returns.html')

def search(request):
    """Global search view"""
    query = request.GET.get('q', '')
    products = Product.objects.none()
    
    if query:
        products = Product.objects.filter(
            is_active=True
        ).filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(tags__icontains=query)
        ).distinct()
    
    context = {
        'query': query,
        'products': products,
        'total_results': products.count(),
    }
    return render(request, 'core/search.html', context)

def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            messages.success(request, 'Thank you for subscribing to our newsletter!')
        else:
            messages.error(request, 'Please enter a valid email address.')
    return redirect('core:home')