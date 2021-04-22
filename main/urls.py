from django.urls import path
from . import views

from django.conf.urls import url

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
    path("admin-panel", views.admin_panel, name="admin-panel"),
    path("filter-data", views.filter_data, name="filter_data"),
    path("add-to-cart-<int:pro_id>/", AddToCartView.as_view(), name="addtocart"),
    path("my-cart/", MyCartView.as_view(), name="mycart"),
    path("manage-cart/<int:cp_id>", ManageCartView.as_view(), name="managecart"),
    path("empty-cart/", EmptyCartView.as_view(), name="emptycart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("register/",
         CustomerRegistrationView.as_view(), name="customerregistration"),

    path("logout/", CustomerLogoutView.as_view(), name="customerlogout"),
    path("login/", CustomerLoginView.as_view(), name="customerlogin"),

    path("profile-<int:id>", CustomerProfileView.as_view(), name="customerprofile"),

    url(r'^products/$', views.product_rest_list),
    path("addToFavourite-<int:id>", views.add_to_favourite, name="addToFavourite"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)