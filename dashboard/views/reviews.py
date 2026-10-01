from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from reviews.models import Review
from dashboard.decorators import staff_required


@staff_required
def review_list(request):
    reviews = Review.objects.select_related('product', 'user').order_by('-created_at')
    status = request.GET.get('status')
    if status == 'pending':
        reviews = reviews.filter(is_approved=False)
    elif status == 'approved':
        reviews = reviews.filter(is_approved=True)

    return render(request, 'dashboard/reviews/list.html', {
        'reviews': reviews, 'active_page': 'reviews',
        'current_status': status,
    })


@staff_required
def review_approve(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.is_approved = True
        review.save()
        messages.success(request, 'Review approved.')
    return redirect('dashboard:review_list')


@staff_required
def review_reject(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review rejected and deleted.')
    return redirect('dashboard:review_list')
