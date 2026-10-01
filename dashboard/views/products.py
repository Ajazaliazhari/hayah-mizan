from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.text import slugify
from django.db import transaction
from catalog.models import Product, Category, Brand, ProductVariant
from dashboard.decorators import staff_required


@staff_required
def product_list(request):
    products = Product.objects.select_related('category', 'brand').order_by('-created_at')

    q = request.GET.get('q')
    if q:
        products = products.filter(name__icontains=q)

    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, 'dashboard/products/list.html', {
        'products': products,
        'categories': Category.objects.filter(is_active=True),
        'active_page': 'products',
    })


@staff_required
def product_create(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                name = request.POST.get('name', '').strip()
                slug = request.POST.get('slug', '').strip() or slugify(name)
                sku = request.POST.get('sku', '').strip()
                category_id = request.POST.get('category')
                brand_id = request.POST.get('brand') or None
                description = request.POST.get('description', '').strip()
                short_description = request.POST.get('short_description', '').strip()
                price = request.POST.get('price')
                compare_at_price = request.POST.get('compare_at_price') or None
                gender = request.POST.get('gender', 'U')
                material = request.POST.get('material', '').strip()
                care_instructions = request.POST.get('care_instructions', '').strip()
                fit = request.POST.get('fit', '').strip()
                meta_title = request.POST.get('meta_title', '').strip()
                meta_description = request.POST.get('meta_description', '').strip()
                is_active = request.POST.get('is_active') == 'on'
                is_featured = request.POST.get('is_featured') == 'on'
                is_new = request.POST.get('is_new') == 'on'
                is_best_seller = request.POST.get('is_best_seller') == 'on'
                is_trending = request.POST.get('is_trending') == 'on'

                if not all([name, sku, category_id, price]):
                    messages.error(request, 'Name, SKU, category, and price are required.')
                    return redirect('dashboard:product_create')

                product = Product(
                    name=name, slug=slug, sku=sku,
                    category_id=category_id, brand_id=brand_id,
                    description=description, short_description=short_description,
                    price=price, compare_at_price=compare_at_price,
                    gender=gender, material=material,
                    care_instructions=care_instructions, fit=fit,
                    meta_title=meta_title, meta_description=meta_description,
                    is_active=is_active, is_featured=is_featured,
                    is_new=is_new, is_best_seller=is_best_seller,
                    is_trending=is_trending,
                )
                if request.FILES.get('main_image'):
                    product.main_image = request.FILES['main_image']
                product.save()

                # Add variants
                colors = request.POST.getlist('variant_color')
                sizes = request.POST.getlist('variant_size')
                quantities = request.POST.getlist('variant_quantity')
                prices = request.POST.getlist('variant_price')

                for i in range(len(colors)):
                    if not colors[i] or not sizes[i]:
                        continue
                    ProductVariant.objects.create(
                        product=product,
                        sku=f'{sku}-{colors[i][:3].upper()}-{sizes[i]}',
                        color=colors[i],
                        size=sizes[i],
                        quantity=int(quantities[i] or 0),
                        price=prices[i] or None,
                    )

                messages.success(request, f'Product "{name}" created with {len(colors)} variants.')
                return redirect('dashboard:product_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    return render(request, 'dashboard/products/form.html', {
        'categories': Category.objects.filter(is_active=True),
        'brands': Brand.objects.filter(is_active=True),
        'active_page': 'products', 'action': 'Create',
    })


@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                product.name = request.POST.get('name', '').strip()
                product.slug = request.POST.get('slug', '').strip() or slugify(product.name)
                product.sku = request.POST.get('sku', '').strip()
                product.category_id = request.POST.get('category')
                product.brand_id = request.POST.get('brand') or None
                product.description = request.POST.get('description', '').strip()
                product.short_description = request.POST.get('short_description', '').strip()
                product.price = request.POST.get('price')
                product.compare_at_price = request.POST.get('compare_at_price') or None
                product.gender = request.POST.get('gender', 'U')
                product.material = request.POST.get('material', '').strip()
                product.care_instructions = request.POST.get('care_instructions', '').strip()
                product.fit = request.POST.get('fit', '').strip()
                product.meta_title = request.POST.get('meta_title', '').strip()
                product.meta_description = request.POST.get('meta_description', '').strip()
                product.is_active = request.POST.get('is_active') == 'on'
                product.is_featured = request.POST.get('is_featured') == 'on'
                product.is_new = request.POST.get('is_new') == 'on'
                product.is_best_seller = request.POST.get('is_best_seller') == 'on'
                product.is_trending = request.POST.get('is_trending') == 'on'

                if request.FILES.get('main_image'):
                    product.main_image = request.FILES['main_image']
                product.save()

                # Update variants
                variant_ids = request.POST.getlist('variant_id')
                colors = request.POST.getlist('variant_color')
                sizes = request.POST.getlist('variant_size')
                quantities = request.POST.getlist('variant_quantity')
                prices = request.POST.getlist('variant_price')
                variant_actives = request.POST.getlist('variant_is_active')

                for i, variant_id in enumerate(variant_ids):
                    if not variant_id:
                        continue
                    try:
                        variant = ProductVariant.objects.get(id=variant_id, product=product)
                        variant.color = colors[i]
                        variant.size = sizes[i]
                        variant.quantity = int(quantities[i] or 0)
                        variant.price = prices[i] or None
                        variant.is_active = i < len(variant_actives) and variant_actives[i] == 'on'
                        variant.save()
                    except ProductVariant.DoesNotExist:
                        pass

                # Add new variants
                new_colors = request.POST.getlist('new_variant_color')
                new_sizes = request.POST.getlist('new_variant_size')
                new_quantities = request.POST.getlist('new_variant_quantity')
                new_prices = request.POST.getlist('new_variant_price')

                for i in range(len(new_colors)):
                    if not new_colors[i] or not new_sizes[i]:
                        continue
                    ProductVariant.objects.create(
                        product=product,
                        sku=f'{product.sku}-{new_colors[i][:3].upper()}-{new_sizes[i]}',
                        color=new_colors[i],
                        size=new_sizes[i],
                        quantity=int(new_quantities[i] or 0),
                        price=new_prices[i] or None,
                    )

                messages.success(request, f'Product "{product.name}" updated.')
                return redirect('dashboard:product_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    return render(request, 'dashboard/products/form.html', {
        'product': product,
        'variants': product.variants.all(),
        'categories': Category.objects.filter(is_active=True),
        'brands': Brand.objects.filter(is_active=True),
        'active_page': 'products', 'action': 'Edit',
    })


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted.')
    return redirect('dashboard:product_list')


@staff_required
def variant_delete(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    product_pk = variant.product.pk
    if request.method == 'POST':
        variant.delete()
        messages.success(request, 'Variant deleted.')
    return redirect('dashboard:product_edit', pk=product_pk)
