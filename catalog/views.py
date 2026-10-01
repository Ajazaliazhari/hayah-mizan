from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max, Count, Avg
from django.http import JsonResponse
from .models import Product, Category, Brand, ProductVariant

def product_list(request):
    """Product listing with filters"""
    products = Product.objects.filter(is_active=True).prefetch_related('variants')
    
    # Get filter parameters
    category_slug = request.GET.get('category')
    brand_slug = request.GET.get('brand')
    gender = request.GET.get('gender')
    size = request.GET.get('size')
    color = request.GET.get('color')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', '-created_at')
    search_query = request.GET.get('q', '')
    
    # Apply filters
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    
    if gender:
        products = products.filter(gender=gender)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    if size:
        products = products.filter(variants__size=size, variants__is_active=True)
    
    if color:
        products = products.filter(variants__color__icontains=color, variants__is_active=True)
    
    # Sorting
    sort_options = {
        'newest': '-created_at',
        'price_low': 'price',
        'price_high': '-price',
        'name': 'name',
        'rating': '-average_rating',
        'popularity': '-total_reviews',
    }
    products = products.order_by(sort_options.get(sort_by, '-created_at'))
    products = products.distinct()
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    context = {
        'page_obj': page_obj,
        'products': page_obj,
        'categories': Category.objects.filter(is_active=True),
        'brands': Brand.objects.filter(is_active=True),
        'sizes': ProductVariant.objects.filter(is_active=True).values_list('size', flat=True).distinct(),
        'colors': ProductVariant.objects.filter(is_active=True).values_list('color', flat=True).distinct(),
        'price_range': Product.objects.filter(is_active=True).aggregate(
            min_price=Min('price'), max_price=Max('price')
        ),
        'current_filters': {
            'category': category_slug,
            'brand': brand_slug,
            'gender': gender,
            'size': size,
            'color': color,
            'min_price': min_price,
            'max_price': max_price,
            'sort': sort_by,
            'q': search_query,
        },
        'total_count': products.count(),
    }
    
    # HTMX partial response
    if request.headers.get('HX-Request'):
        return render(request, 'catalog/partials/product_grid.html', context)
    
    return render(request, 'catalog/product_list.html', context)

def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(
        Product.objects.prefetch_related('variants', 'reviews'),
        slug=slug, is_active=True
    )
    
    # Get variants grouped by color
    variants = product.variants.filter(is_active=True)
    colors = variants.values_list('color', flat=True).distinct()
    sizes = variants.values_list('size', flat=True).distinct()
    
    # Build color-size availability matrix
    variant_matrix = {}
    for variant in variants:
        if variant.color not in variant_matrix:
            variant_matrix[variant.color] = {}
        variant_matrix[variant.color][variant.size] = {
            'id': variant.id,
            'in_stock': variant.is_in_stock,
            'quantity': variant.available_quantity,
            'price': str(variant.effective_price),
            'sku': variant.sku,
        }
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    
    # Recently viewed
    recently_viewed = request.session.get('recently_viewed', [])
    if product.id not in recently_viewed:
        recently_viewed.insert(0, product.id)
        recently_viewed = recently_viewed[:10]
        request.session['recently_viewed'] = recently_viewed
    recent_products = Product.objects.filter(id__in=recently_viewed).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'variants': variants,
        'colors': colors,
        'sizes': sizes,
        'variant_matrix': variant_matrix,
        'related_products': related_products,
        'recent_products': recent_products,
        'reviews': product.reviews.filter(is_approved=True)[:10],
    }
    return render(request, 'catalog/product_detail.html', context)

def category_detail(request, slug):
    """Category detail page"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Include subcategory products
    subcategories = category.children.filter(is_active=True)
    if subcategories:
        products = Product.objects.filter(
            Q(category=category) | Q(category__in=subcategories),
            is_active=True
        )
    
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'subcategories': subcategories,
    }
    return render(request, 'catalog/category_detail.html', context)

def get_variant_details(request, variant_id):
    """AJAX endpoint to get variant details"""
    try:
        variant = ProductVariant.objects.get(id=variant_id, is_active=True)
        return JsonResponse({
            'success': True,
            'variant': {
                'id': variant.id,
                'sku': variant.sku,
                'price': str(variant.effective_price),
                'compare_at_price': str(variant.effective_compare_at_price) if variant.effective_compare_at_price else None,
                'quantity': variant.available_quantity,
                'in_stock': variant.is_in_stock,
                'color': variant.color,
                'size': variant.size,
                'image': variant.image.url if variant.image else variant.product.main_image.url,
            }
        })
    except ProductVariant.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Variant not found'}, status=404)

def quick_view(request, slug):
    """Quick view modal for product"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'catalog/partials/quick_view.html', {'product': product})