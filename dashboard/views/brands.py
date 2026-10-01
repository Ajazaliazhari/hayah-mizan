from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.text import slugify
from catalog.models import Brand
from dashboard.decorators import staff_required


@staff_required
def brand_list(request):
    brands = Brand.objects.all().order_by('name')
    return render(request, 'dashboard/brands/list.html', {
        'brands': brands, 'active_page': 'brands',
    })


@staff_required
def brand_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip() or slugify(name)
        description = request.POST.get('description', '').strip()
        website = request.POST.get('website', '').strip()
        is_active = request.POST.get('is_active') == 'on'

        if not name:
            messages.error(request, 'Name is required.')
            return redirect('dashboard:brand_create')

        brand = Brand(name=name, slug=slug, description=description,
                      website=website, is_active=is_active)
        if request.FILES.get('logo'):
            brand.logo = request.FILES['logo']
        brand.save()
        messages.success(request, f'Brand "{name}" created.')
        return redirect('dashboard:brand_list')

    return render(request, 'dashboard/brands/form.html', {
        'active_page': 'brands', 'action': 'Create',
    })


@staff_required
def brand_edit(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        brand.name = request.POST.get('name', '').strip()
        brand.slug = request.POST.get('slug', '').strip() or slugify(brand.name)
        brand.description = request.POST.get('description', '').strip()
        brand.website = request.POST.get('website', '').strip()
        brand.is_active = request.POST.get('is_active') == 'on'
        if request.FILES.get('logo'):
            brand.logo = request.FILES['logo']
        brand.save()
        messages.success(request, f'Brand "{brand.name}" updated.')
        return redirect('dashboard:brand_list')

    return render(request, 'dashboard/brands/form.html', {
        'brand': brand, 'active_page': 'brands', 'action': 'Edit',
    })


@staff_required
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        name = brand.name
        brand.delete()
        messages.success(request, f'Brand "{name}" deleted.')
    return redirect('dashboard:brand_list')
