from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum
from accounts.models import User
from orders.models import Order
from dashboard.decorators import staff_required


@staff_required
def customer_list(request):
    customers = User.objects.filter(is_staff=False).annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total_amount'),
    ).order_by('-date_joined')

    q = request.GET.get('q')
    if q:
        customers = customers.filter(email__icontains=q) | customers.filter(username__icontains=q)

    return render(request, 'dashboard/customers/list.html', {
        'customers': customers, 'active_page': 'customers',
    })


@staff_required
def customer_detail(request, pk):
    customer = get_object_or_404(User, pk=pk)
    orders = Order.objects.filter(user=customer).order_by('-created_at')
    return render(request, 'dashboard/customers/detail.html', {
        'customer': customer,
        'orders': orders,
        'active_page': 'customers',
    })
