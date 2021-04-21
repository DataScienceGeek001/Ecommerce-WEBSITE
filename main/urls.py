from django.urls import path
from . import views

from .views import *

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('search', views.search, name='search'),
    path('category-list', views.category_list, name='category-list'),
    path('brand-list', views.brand_list, name='brand-list'),
    path('product-list', views.product_list, name='product-list'),
    path('category-product-list/<int:cat_id>', views.category_product_list, name='category-product-list'),
    path('brand-product-list/<int:brand_id>', views.brand_product_list, name='brand-product-list'),
    path('product/<str:slug>/<int:id>', views.product_detail, name='product-detail'),
    path('register', views.register_request, name='register'),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name= "logout"),
    path("admin-panel", views.admin_panel, name="admin-panel"),
    path("filter-data", views.filter_data, name="filter_data"),
    path("add-to-cart-<int:pro_id>/", AddToCartView.as_view(), name="addtocart"),
    path("my-cart/", MyCartView.as_view(), name="mycart"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)