from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Entry, Category

# Create your views here.

class CategoryListView(ListView):
    model = Category
    context_object_name = 'category_list'
