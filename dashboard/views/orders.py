from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from orders.models import Order, OrderEvent
from dashboard.decorators import staff_required


@staff_required
def order_list(request):
    orders = Order.objects.select_related('user').order_by('-created_at')

    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    q = request.GET.get('q')
    if q:
        orders = orders.filter(order_number__icontains=q)

    return render(request, 'dashboard/orders/list.html', {
        'orders': orders,
        'active_page': 'orders',
        'current_status': status,
        'statuses': Order.ORDER_STATUS,
    })


@staff_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        tracking_number = request.POST.get('tracking_number', '').strip()
        carrier = request.POST.get('carrier', '').strip()
        admin_notes = request.POST.get('admin_notes', '').strip()

        if new_status and new_status != order.status:
            OrderEvent.objects.create(
                order=order, status=new_status,
                description=f'Status updated by admin to {new_status}',
                created_by=request.user,
            )
            order.status = new_status
            if new_status == 'shipped':
                from django.utils import timezone
                order.shipped_at = timezone.now()
            elif new_status == 'delivered':
                from django.utils import timezone
                order.delivered_at = timezone.now()

        if tracking_number:
            order.tracking_number = tracking_number
        if carrier:
            order.carrier = carrier
        if admin_notes:
            order.admin_notes = admin_notes

        order.save()
        messages.success(request, 'Order updated.')
        return redirect('dashboard:order_detail', order_number=order.order_number)

    return render(request, 'dashboard/orders/detail.html', {
        'order': order,
        'active_page': 'orders',
        'statuses': Order.ORDER_STATUS,
    })
