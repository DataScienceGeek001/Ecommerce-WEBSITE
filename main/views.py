from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import Category, Brand, Product, ProductAttribute, Banner

from .models import *

from django.db.models import Max, Min, Count
from django.template.loader import render_to_string

from django.urls import reverse_lazy, reverse

from .forms import *
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from django.views.generic import View, TemplateView, CreateView, FormView, ListView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# For Password Reset
from .utils import password_reset_token
from django.core.mail import send_mail
from django.conf import settings

import razorpay
from django.views.decorators.csrf import csrf_exempt

# REST FRAMEWORK TESTING
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .main_serializer import ProductSerializer

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def product_rest_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return JSONResponse(serializer.data)

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
    is_favourite = False
    # if product.favourite.filter(id=request.customer.id).exists():
    #     is_favourite = True
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:3]
    return render(request, 'product_detail.html', {'data': product, 'related': related_products})


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


@method_decorator(login_required(login_url="/login/"), name='dispatch')
class AddToCartView(EcomMixin, TemplateView):
    template_name = "addtocart.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['pro_id']
        # get product
        product_obj = Product.objects.get(id=product_id)
        # print(product_obj.price)
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
                messages.success(self.request, 'Product Added to cart successfully!')
            # new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.price, quantity=1, subtotal=product_obj.price)
                cart_obj.total += product_obj.price
                cart_obj.save()
                messages.success(self.request, 'Product Added to cart successfully!')

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj, product=product_obj, rate=product_obj.price, quantity=1, subtotal=product_obj.price)
            cart_obj.total += product_obj.price
            cart_obj.save()
            messages.success(self.request, 'Product Added to cart successfully!')

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
    success_url = 'home'

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
            pm = form.cleaned_data.get("payment_method")
            order = form.save()
            if pm == "Razorpay":
                return redirect(reverse("razorpayrequest") + "?o_id=" + str(order.id))

        else:
            return redirect("home")
        return super().form_valid(form)

class RazorpayRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        client = razorpay.Client(
            auth=("rzp_test_ejxwUwJ32rcHr9", "NyZiMrNZQSE6yHStcTvTo63a"))

        payment = client.order.create({'amount': order.total, 'currency': 'INR', 'payment_capture': '1'})
        context = {
            "order": order 
        }
        return context


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

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is None:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})
        if usr.is_superuser:
            login(self.request, usr)
            return redirect("adminhome")
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
        favorites = Product.objects.filter(favorite=customer)
        context["favorites"] = favorites
        return context

@login_required(login_url='/login/')
def add_to_favourite(request, id):
    # print(id)
    product = get_object_or_404(Product, id=id)
    if product.favorite.filter(id=request.user.customer.id).exists():
        print(request.user.customer)
        product.favorite.remove(request.user.customer)
    else:
        product.favorite.add(request.user.customer)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            pass
        else:
            return redirect("/login/")
        return super().dispatch(request, *args, **kwargs)

class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "adminhome.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = Customer.objects.all()
        context['products'] = Product.objects.all()
        context["pendingorders"] = Order.objects.filter(order_status="Order Received").order_by("-id")
        return context

class DeleteCustomer(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        print("This is User Section for Admin")
        user_id = self.kwargs["cust_id"]
        user_obj = User.objects.get(id=user_id)
        if user_obj:
            user_obj.delete()
        else:
            pass
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class DeleteProduct(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        print("This is Product Section for Admin")
        prod_id = self.kwargs["prod_id"]
        print(prod_id)
        prod_obj = Product.objects.get(id=prod_id)
        print(prod_obj)
        if prod_obj:
            prod_obj.delete()
        else:
            pass
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class AdminOrderDetails(AdminRequiredMixin, TemplateView):
    template_name = "adminOrderDetails.html"

    def get_context_data(self, **kwargs):
        print("This is Order Details for Admin")
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs["ord_id"]
        print(order_id)
        order_obj = Order.objects.get(id=order_id)
        context['order'] = order_obj
        context['statuses'] = ORDER_STATUS
        return context

class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = "adminorderlist.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"
    # paginate_by = 3


class AdminOrderStatusChange(AdminRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):
        ord_id = self.kwargs['ord_id']
        ord_obj = Order.objects.get(id=ord_id)
        print("This is Order Status Change View")
        print(ord_id, ord_obj)
        new_status = request.POST.get('status')
        ord_obj.order_status = new_status
        ord_obj.save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class PasswordForgotView(FormView):
    template_name = "forgotpassword.html"
    form_class = PasswordForgotForm
    success_url = "/login/"

    def form_valid(self, form):
        # get email from user
        email = form.cleaned_data.get("email")
        # get current host ip/domain
        url = self.request.META['HTTP_HOST']
        # get customer and then user
        customer = Customer.objects.get(user__email=email)
        user = customer.user
        # send mail to the user with email
        text_content = 'Please Click the link below to reset your password. '
        html_content = url + "/password-reset/" + email + \
            "/" + password_reset_token.make_token(user) + "/"
        send_mail(
            'Password Reset Link | Django Ecommerce',
            text_content + html_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return super().form_valid(form)

class PasswordResetView(FormView):
    template_name = "passwordreset.html"
    form_class = PasswordResetForm
    success_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        token = self.kwargs.get("token")
        if user is not None and password_reset_token.check_token(user, token):
            pass
        else:
            return redirect(reverse("passwordforgot"))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        password = form.cleaned_data['new_password']
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return super().form_valid(form)

class AddProductView(AdminRequiredMixin, FormView):
    template_name = "addProducts.html"
    form_class = ProductAddForm
    success_url = "admin-product-list"

    def form_valid(self, form):
        title = form.cleaned_data.get("title")
        slug = form.cleaned_data.get("slug")
        details = form.cleaned_data.get("details")
        specs = form.cleaned_data.get("specs")
        category = form.cleaned_data.get("category")
        brand = form.cleaned_data.get("brand")
        price = form.cleaned_data.get("price")
        is_featured = form.cleaned_data.get("is_featured")
        
        form.save()
        
        return super().form_valid(form)

class AddProductAttributeView(AdminRequiredMixin, FormView):
    template_name = "addProductAttributes.html"
    form_class = ProductAttributeForm
    success_url = "admin-product-list"

    def form_valid(self, form):
        product = form.cleaned_data.get("product")
        color = form.cleaned_data.get("color")
        size = form.cleaned_data.get("size")
        image = form.cleaned_data.get("image")
        p = ProductAttribute.objects.create(product=product, color=color, size=size, image = image)
        p.save
        return super().form_valid(form)

@csrf_exempt
def success(request):
    # del request.session['cart_id']
    return render(request, "success.html")

class AdminProductListView(AdminRequiredMixin, ListView):
    template_name = 'adminProductList.html'
    queryset = Product.objects.all().order_by("-id")
    context_object_name = "products"

class AdminBrandListView(AdminRequiredMixin, ListView):
    template_name = 'adminBrandList.html'
    queryset = Brand.objects.all().order_by("-id")
    context_object_name = "brands"

class AdminCategoryListView(AdminRequiredMixin, ListView):
    template_name = 'adminCategoryList.html'
    queryset = Category.objects.all().order_by("-id")
    context_object_name = "categorys"


class AdminUserListView(AdminRequiredMixin, ListView):
    template_name = 'adminUserList.html'
    queryset = Customer.objects.all().order_by("-id")
    context_object_name = "customers"

class AddBrandView(AdminRequiredMixin, FormView):
    template_name = "addBrand.html"
    form_class = BrandAddForm
    success_url = "admin-brand-list"

    def form_valid(self, form):
        title = form.cleaned_data.get("title")
        image = form.cleaned_data.get("image")
        form.save()
        return super().form_valid(form)

class AddCategoryView(AdminRequiredMixin, FormView):
    template_name = "addCategory.html"
    form_class = CategoryAddForm
    success_url = "admin-category-list"

    def form_valid(self, form):
        title = form.cleaned_data.get("title")
        image = form.cleaned_data.get("image")
        form.save()
        return super().form_valid(form)

class AddCustomerView(AdminRequiredMixin, FormView):
    template_name = "addCustomer.html"
    form_class = CustomerRegistrationForm
    success_url = "admin-user-list"

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        form.save()
        return super().form_valid(form)

class ProductUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "productUpdateForm.html"
    model = Product
    fields = [
        "title", "slug", "details", "specs", "category", "brand", "price", "is_featured"
    ]
    success_url = "admin-product-list"

class BrandUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "brandUpdateForm.html"
    model = Brand
    fields = [
        "title", "image"
    ]
    success_url = "admin-brand-list"

class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "categoryUpdateForm.html"
    model = Category
    fields = [
        "title", "image"
    ]
    success_url = "admin-category-list"

class UserUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "userUpdateForm.html"
    model = User
    fields = [
        "username", "password", "email", "full_name", "address"
    ]
    success_url = "admin-user-list"