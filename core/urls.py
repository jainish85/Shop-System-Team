# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. Home Pages
    path('', views.home, name='index'),
    path('home/', views.home, name='home'),

    # 2. Product Actions
    path('add-product/', views.add_product, name='add_product'),
    path('add-category/', views.add_category, name='add_category'),
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),

    # 3. NEW: Manage Categories (This fixes your current error)
    path('categories/', views.manage_categories, name='manage_categories'),
    path('delete-category/<int:pk>/', views.delete_category, name='delete_category'),

    # 4. NEW: Product Detail (This is your 5th page for the report)
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('sell/<int:pk>/', views.sell_product, name='sell_product'),
    path('sales-history/', views.sales_history, name='sales_history'),
    path('profile/', views.profile, name='profile'),

    path('expenses/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('expenses/', views.expenses_view, name='expenses'),
]