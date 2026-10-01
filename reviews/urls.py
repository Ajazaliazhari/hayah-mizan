from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<slug:product_slug>/', views.add_review, name='add'),
    path('<int:review_id>/helpful/', views.mark_helpful, name='helpful'),
    path('<int:review_id>/not-helpful/', views.mark_not_helpful, name='not_helpful'),
]