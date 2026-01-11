from django.contrib import admin
from .models import Category, Product

# This tells Django: "Show these tables in the Admin Panel"
admin.site.register(Category)
admin.site.register(Product)