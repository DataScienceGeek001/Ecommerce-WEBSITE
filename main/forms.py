from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import *

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["ordered_by", "shipping_address",
                  "mobile", "email"]

class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())

    class Meta:
        model = Customer
        fields = ["username", "password", "email", "full_name", "address"]

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError(
                "Customer with this username already exists.")

        return uname


class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if User.objects.filter(username=uname).exists():
            pass
        else:
            raise forms.ValidationError(
                "*Customer with this username does not exist.")

        return uname

class PasswordForgotForm(forms.Form):
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter the mail used in your account...."
            }))

    def clean_email(self):
        e = self.cleaned_data.get("email")
        if Customer.objects.filter(user__email=e).exists():
            pass
        else:
            raise forms.ValidationError(
                "Customer with this email does not exist. Please try again!"
            )
        return e
        
class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'new-password',
        'placeholder': 'Enter New Password',
    }), label="New Password")
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'new-password',
        'placeholder': 'Confirm New Password',
    }), label="Confirm New Password")

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data.get("new_password")
        confirm_new_password = self.cleaned_data.get("confirm_new_password")
        if new_password != confirm_new_password:
            raise forms.ValidationError(
                "Passwords did not match!")
        return confirm_new_password

class ProductAddForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput())
    slug = forms.CharField(widget=forms.TextInput())
    details = forms.CharField(widget=forms.Textarea)
    specs = forms.CharField(widget=forms.Textarea)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), required=True)
    price = forms.IntegerField(widget=forms.NumberInput())
    is_featured = forms.BooleanField(required=False,initial=False,label='Featured')

    class Meta:
        model = Product
        fields = ["title", "slug", "details",
                  "specs", "category", "brand",
                  "price", "is_featured"]
    
class ProductAttributeForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    color = forms.ModelChoiceField(queryset=Color.objects.all())
    size = forms.ModelChoiceField(queryset=Size.objects.all())
    image = forms.FileField()
    
    class Meta:
        model = ProductAttribute
        fields = ["product", "color", "size", "image"]