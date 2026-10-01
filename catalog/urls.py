from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<slug:slug>/quick-view/', views.quick_view, name='quick_view'),
    path('variant/<int:variant_id>/', views.get_variant_details, name='variant_details'),
]