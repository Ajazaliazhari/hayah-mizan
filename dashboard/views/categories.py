from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.text import slugify
from catalog.models import Category
from dashboard.decorators import staff_required


@staff_required
def category_list(request):
    categories = Category.objects.all().order_by('order', 'name')
    return render(request, 'dashboard/categories/list.html', {
        'categories': categories, 'active_page': 'categories',
    })


@staff_required
def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip() or slugify(name)
        description = request.POST.get('description', '').strip()
        parent_id = request.POST.get('parent') or None
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')

        if not name:
            messages.error(request, 'Name is required.')
            return redirect('dashboard:category_create')

        category = Category(
            name=name, slug=slug, description=description,
            parent_id=parent_id if parent_id else None,
            order=int(order or 0), is_active=is_active,
        )
        if image:
            category.image = image
        category.save()
        messages.success(request, f'Category "{name}" created successfully.')
        return redirect('dashboard:category_list')

    return render(request, 'dashboard/categories/form.html', {
        'active_page': 'categories',
        'parents': Category.objects.filter(parent=None),
        'action': 'Create',
    })


@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.name = request.POST.get('name', '').strip()
        category.slug = request.POST.get('slug', '').strip() or slugify(category.name)
        category.description = request.POST.get('description', '').strip()
        parent_id = request.POST.get('parent') or None
        category.parent_id = parent_id if parent_id else None
        category.order = int(request.POST.get('order', 0) or 0)
        category.is_active = request.POST.get('is_active') == 'on'

        if request.FILES.get('image'):
            category.image = request.FILES['image']

        category.save()
        messages.success(request, f'Category "{category.name}" updated.')
        return redirect('dashboard:category_list')

    return render(request, 'dashboard/categories/form.html', {
        'category': category,
        'parents': Category.objects.filter(parent=None).exclude(pk=pk),
        'active_page': 'categories',
        'action': 'Edit',
    })


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted.')
    return redirect('dashboard:category_list')
