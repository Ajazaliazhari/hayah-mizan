from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Review
from catalog.models import Product

@login_required
def add_review(request, product_slug):
    """Add a review"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    
    # Check if user already reviewed
    existing = Review.objects.filter(product=product, user=request.user).first()
    if existing:
        messages.warning(request, 'You have already reviewed this product.')
        return redirect('catalog:product_detail', slug=product_slug)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        title = request.POST.get('title', '')
        comment = request.POST.get('comment', '')
        
        Review.objects.create(
            product=product, user=request.user,
            rating=rating, title=title, comment=comment,
        )
        messages.success(request, 'Review submitted! It will appear after moderation.')
        return redirect('catalog:product_detail', slug=product_slug)
    
    return render(request, 'reviews/add_review.html', {'product': product})

@require_POST
def mark_helpful(request, review_id):
    """Mark review as helpful"""
    review = get_object_or_404(Review, id=review_id, is_approved=True)
    review.helpful_count += 1
    review.save()
    return JsonResponse({'success': True, 'helpful_count': review.helpful_count})

@require_POST
def mark_not_helpful(request, review_id):
    """Mark review as not helpful"""
    review = get_object_or_404(Review, id=review_id, is_approved=True)
    review.not_helpful_count += 1
    review.save()
    return JsonResponse({'success': True, 'not_helpful_count': review.not_helpful_count})