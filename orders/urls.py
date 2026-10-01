from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('place/', views.place_order, name='place_order'),
    path('', views.order_list, name='list'),
    path('<str:order_number>/', views.order_detail, name='detail'),
    path('<str:order_number>/confirmation/', views.order_confirmation, name='confirmation'),
    path('<str:order_number>/cancel/', views.cancel_order, name='cancel'),
    path('<str:order_number>/return/', views.request_return, name='request_return'),
]