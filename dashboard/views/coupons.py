from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from promotions.models import Coupon
from dashboard.decorators import staff_required


@staff_required
def coupon_list(request):
    coupons = Coupon.objects.all().order_by('-created_at')
    return render(request, 'dashboard/coupons/list.html', {
        'coupons': coupons, 'active_page': 'coupons',
    })


@staff_required
def coupon_create(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        if Coupon.objects.filter(code=code).exists():
            messages.error(request, f'Coupon code "{code}" already exists.')
            return redirect('dashboard:coupon_create')

        coupon = Coupon(
            code=code,
            description=request.POST.get('description', '').strip(),
            discount_type=request.POST.get('discount_type', 'percentage'),
            discount_value=request.POST.get('discount_value') or 0,
            min_cart_value=request.POST.get('min_cart_value') or 0,
            max_discount=request.POST.get('max_discount') or None,
            usage_limit=request.POST.get('usage_limit') or None,
            usage_limit_per_user=request.POST.get('usage_limit_per_user') or 1,
            first_order_only=request.POST.get('first_order_only') == 'on',
            is_active=request.POST.get('is_active') == 'on',
        )
        valid_until = request.POST.get('valid_until')
        if valid_until:
            coupon.valid_until = parse_datetime(valid_until) or None
        coupon.save()
        messages.success(request, f'Coupon "{code}" created.')
        return redirect('dashboard:coupon_list')

    return render(request, 'dashboard/coupons/form.html', {
        'active_page': 'coupons', 'action': 'Create',
    })


@staff_required
def coupon_edit(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        coupon.code = request.POST.get('code', '').strip().upper()
        coupon.description = request.POST.get('description', '').strip()
        coupon.discount_type = request.POST.get('discount_type', 'percentage')
        coupon.discount_value = request.POST.get('discount_value') or 0
        coupon.min_cart_value = request.POST.get('min_cart_value') or 0
        coupon.max_discount = request.POST.get('max_discount') or None
        coupon.usage_limit = request.POST.get('usage_limit') or None
        coupon.usage_limit_per_user = request.POST.get('usage_limit_per_user') or 1
        coupon.first_order_only = request.POST.get('first_order_only') == 'on'
        coupon.is_active = request.POST.get('is_active') == 'on'
        valid_until = request.POST.get('valid_until')
        if valid_until:
            coupon.valid_until = parse_datetime(valid_until)
        coupon.save()
        messages.success(request, f'Coupon "{coupon.code}" updated.')
        return redirect('dashboard:coupon_list')

    return render(request, 'dashboard/coupons/form.html', {
        'coupon': coupon, 'active_page': 'coupons', 'action': 'Edit',
    })


@staff_required
def coupon_delete(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        code = coupon.code
        coupon.delete()
        messages.success(request, f'Coupon "{code}" deleted.')
    return redirect('dashboard:coupon_list')
