from django.shortcuts import render
from .models import Category, Brand, Product, ProductAttribute, Banner

# Create your views here.
def home(request):
    banners = Banner.objects.all().order_by('-id')
    data = Product.objects.filter(is_featured=True).order_by('-id')
    return render(request, 'index.html', {'data': data, 'banners': banners})

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
    data = Product.objects.all().order_by('-id')
    # min_price = ProductAttribute.objects.aggregate(min('price'))
    # max_price = ProductAttribute.objects.aggregate(max('price'))
    return render(request, 'product_list.html', 
                {
                    'data': data,
                }
    )

def category_product_list(request, cat_id):
    category = Category.objects.get(id=cat_id)
    data = Product.objects.filter(category=category).order_by('-id')
    return render(request, 'category_product_list.html', {
            'data': data, 
            })

def brand_product_list(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    data = Product.objects.filter(brand=brand).order_by('-id')
    return render(request, 'category_product_list.html', {
            'data': data,
            })

# Product Details
def product_detail(request, slug, id):
    product = Product.objects.get(id=id)
    return render(request, 'product_detail.html', {'data': product})