from django.shortcuts import render
from .models import Category, Brand, Product, ProductAttribute

# Create your views here.
def home(request):
    return render(request, 'index.html')

# Category
def category_list(request):
    data = Category.objects.all().order_by('-id')
    return render(request, 'category_list.html', {'data': data})

# Brand
def brand_list(request):
    brands = Brand.objects.all().order_by('-id')
    return render(request, 'brand_list.html', {'brands': brands})

# Product List
def product_list(request):
    products = Product.objects.all().order_by('-id')
    cats = Product.objects.distinct().values('category__title', 'category__id')
    brands = Product.objects.distinct().values('brand__title', 'brand__id')
    colors = ProductAttribute.objects.distinct().values('color__title', 'color__id', 'color__color_code')
    sizes = ProductAttribute.objects.distinct().values('size__title', 'size__id')

    return render(request, 'product_list.html', 
                {
                    'products': products,
                    'cats': cats,
                    'brands': brands,
                    'colors': colors,
                    'sizes': sizes,
                }
    )