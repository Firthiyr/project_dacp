from django.db import models
from django.utils.text import slugify

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class ProductSize(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="product_sizes"
    )
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.size.name} - ({self.stock} in stock) for {self.product.name}"


class Product(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    color = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    main_image = models.ImageField(upload_to="products/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


def __str__(self):
    return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/extra/")

    def __str__(self):
        return f"Image for {self.product.name}"


class Banner(models.Model):
    title = models.CharField(max_length=200, verbose_name="Title")
    subtitle = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Subtitle"
    )
    image = models.ImageField(upload_to="sliders/", verbose_name="Image (1920x1080)")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    order = models.IntegerField(default=0, verbose_name="Display order")

    button_text = models.CharField(
        max_length=50, default="Shop Now", verbose_name="Text for button"
    )
    button_link = models.CharField(
        max_length=200,
        default="main:catalog_all",
        verbose_name="Link (e.g., main:catalog_all)",
    )

    class Meta:
        verbose_name = "Banner on the main page"
        verbose_name_plural = "Banners on the main page"
        ordering = ["order"]

    def __str__(self):
        return self.title
