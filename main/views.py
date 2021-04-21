from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import Category, Brand, Product, ProductAttribute, Banner

from .models import *

from django.db.models import Max, Min, Count
from django.template.loader import render_to_string

from django.urls import reverse_lazy, reverse

from .forms import NewUserForm, CheckoutForm, CustomerRegistrationForm, CustomerLoginForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from django.views.generic import View, TemplateView, CreateView, FormView
from django.contrib.auth.decorators import login_required

# Create your views here.

class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


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
    return render(request, 'product_list.html', 
                {
                    'data': data,
                })

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
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:3]
    return render(request, 'product_detail.html', {'data': product, 'related': related_products})


def admin_panel(request):
	return render(request, "admin.html")

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration Successful.")
            return redirect("home")
        messages.error(request, "Unsuccessful registratio. Invalid information.")
    form = NewUserForm()
    return render (request=request, template_name="register.html", context={"register_form":form})


def search(request):
    q = request.GET['q']
    data = Product.objects.filter(title__icontains=q).order_by('-id')
    return render(request, 'search.html', {'data': data})


def filter_data(request):
    colors = request.GET.getlist('color[]')
    categories = request.GET.getlist('category[]')
    brands = request.GET.getlist('brand[]')
    sizes = request.GET.getlist('size[]')
    allProducts=Product.objects.all().order_by('-id').distinct()
    
    if len(colors) > 0:
        allProducts = allProducts.filter(productattribute__color__id__in=colors).distinct()

    if len(categories) > 0:
        allProducts = allProducts.filter(category__id__in=categories).distinct()

    if len(brands) > 0:
        allProducts = allProducts.filter(brand__id__in=brands).distinct()

    if len(sizes) > 0:
        allProducts = allProducts.filter(productattribute__size__id__in=sizes).distinct()

    t = render_to_string('ajax/product-list.html', {'data': allProducts})
    
    return JsonResponse({'data': t})


class AddToCartView(EcomMixin, TemplateView):
    template_name = "addtocart.html"
    
    # @login_required
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['pro_id']
        # get product
        product_obj = Product.objects.get(id=product_id)
        print(product_obj.price)
        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        print(cart_id)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(
                product=product_obj)

            # item already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.price
                cartproduct.save()
                cart_obj.total += product_obj.price
                cart_obj.save()
            # new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.price, quantity=1, subtotal=product_obj.price)
                cart_obj.total += product_obj.price
                cart_obj.save()

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj, product=product_obj, rate=product_obj.price, quantity=1, subtotal=product_obj.price)
            cart_obj.total += product_obj.price
            cart_obj.save()

        return context


class MyCartView(EcomMixin, TemplateView):
    template_name = "mycart.html"

    # @login_required(login_url='/login')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context

class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        print("This is Manage Cart Section")
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == 'inc':
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == 'dcr':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == 'rmv':
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass

        return redirect("mycart")

class EmptyCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("mycart")

class CheckoutView(EcomMixin, CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            del self.request.session['cart_id']
        else:
            return redirect("home")
        return super().form_valid(form)


class CustomerRegistrationView(EcomMixin, CreateView):
    template_name = "customerregistration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

class CustomerLogoutView(EcomMixin, View):
    def get(self, request):
        logout(request)
        return redirect("home")


class CustomerLoginView(EcomMixin, FormView):
    template_name = "customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("home")

    # form_valid method is a type of post method and is available in createview formview and updateview
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr.is_superuser:
            login(self.request, usr)
            messages.info(self.request, f"You are now logged in as {uname}.")
            return redirect("admin-panel")
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context
