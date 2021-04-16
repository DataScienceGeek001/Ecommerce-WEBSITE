from django.contrib import admin

# Register your models here.
from .models import Category, Brand, Color, Size, Product, ProductAttribute, Banner

admin.site.register(Banner)
admin.site.register(Size)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_tag')
admin.site.register(Category, CategoryAdmin)

class BrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_tag')
admin.site.register(Brand, BrandAdmin)

class ColorAdmin(admin.ModelAdmin):
    list_display = ('title', 'color_bg')
admin.site.register(Color, ColorAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'brand', 'color', 'size', 'status')
    list_editable = ('status', )
admin.site.register(Product, ProductAdmin)

# Product Attribute
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'price', 'color', 'size')
admin.site.register(ProductAttribute, ProductAttributeAdmin)