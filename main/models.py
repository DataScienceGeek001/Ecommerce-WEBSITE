from django.db import models

# Banner
class Banner(models.Model):
    img = models.CharField(max_length=200)
    alt_text = models.CharField(max_length=300)

    class Meta:
        verbose_name_plural = '1. Banners'


# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="cat_imgs/")

    class Meta:
        verbose_name_plural = '2. Categories'

    def __str__(self):
        return self.title

class Brand(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="brand_imgs/")

    class Meta:
        verbose_name_plural = '3. Brands'

    def __str__(self):
        return self.title

class Color(models.Model):
    title = models.CharField(max_length=100)
    color_code = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = '4. Colors'

    def __str__(self):
        return self.title

class Size(models.Model):
    title = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = '5. Sizes'

    def __str__(self):
        return self.title

# Products
class Product(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="product_imgs/")
    slug = models.CharField(max_length=400)
    details = models.TextField()
    specs = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = '6. Products'

    def __str__(self):
        return self.title

class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = '7. ProductAttributes'

    def __str__(self):
        return self.product.title