import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Category, Brand, Product, ProductVariant
from decimal import Decimal

# Create Categories
men = Category.objects.create(name="Men", slug="men", order=1)
women = Category.objects.create(name="Women", slug="women", order=2)
kids = Category.objects.create(name="Kids", slug="kids", order=3)

# Create Brand
brand = Brand.objects.create(name="HAYAH MIZAN", slug="hayah-mizan")

# Create Products
products_data = [
    {
        'name': 'Classic White Shirt',
        'category': men,
        'price': Decimal('1499.00'),
        'compare_at_price': Decimal('2499.00'),
        'gender': 'M',
        'is_featured': True,
        'is_new': True,
    },
    {
        'name': 'Elegant Black Dress',
        'category': women,
        'price': Decimal('2999.00'),
        'compare_at_price': Decimal('4999.00'),
        'gender': 'F',
        'is_featured': True,
        'is_best_seller': True,
    },
    {
        'name': 'Kids Cotton T-Shirt',
        'category': kids,
        'price': Decimal('599.00'),
        'gender': 'K',
        'is_new': True,
    },
]

for i, pdata in enumerate(products_data, 1):
    product = Product.objects.create(
        sku=f'HM-{i:04d}',
        description='Premium quality fabric with modern design. Perfect for any occasion.',
        short_description='Premium quality, modern design.',
        brand=brand,
        **pdata
    )
    # Create variants
    for color in ['Black', 'White', 'Navy']:
        for size in ['S', 'M', 'L', 'XL']:
            ProductVariant.objects.create(
                product=product,
                sku=f'{product.sku}-{color[:2].upper()}-{size}',
                color=color,
                size=size,
                quantity=20,
            )

print("✅ Sample data created successfully!")