from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class VendorType(models.TextChoices):
    DRINKS = 'drinks', 'Drinks'
    FOOD = 'food', 'Food'

class Vendor(models.Model):
    name = models.CharField(max_length=100)
    vendor_type = models.CharField(max_length=10, choices=VendorType.choices)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_vendors')
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['vendor_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_vendor_type_display()})"

class Category(models.Model):
    name = models.CharField(max_length=50)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='categories')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'Categories'
        unique_together = ['vendor', 'name']

    def __str__(self):
        try:
            return f"{self.vendor.name} - {self.name}"
        except AttributeError:
            return f"Category: {self.name}"

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    preparation_time = models.PositiveIntegerField(help_text="Preparation time in minutes", default=15)
    ingredients = models.TextField(blank=True, help_text="List of ingredients")
    calories = models.PositiveIntegerField(null=True, blank=True)
    is_spicy = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = ['category', 'name']

    def __str__(self):
        try:
            return f"{self.category.vendor.name} - {self.name}"
        except AttributeError:
            return f"MenuItem: {self.name}"

    @property
    def vendor(self):
        try:
            return self.category.vendor
        except AttributeError:
            return None

class Table(models.Model):
    number = models.PositiveIntegerField(unique=True, validators=[MinValueValidator(1), MaxValueValidator(999)])
    seats = models.PositiveIntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(12)])
    is_active = models.BooleanField(default=True)
    qr_code = models.ImageField(upload_to='table_qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Table {self.number}"

    @property
    def is_occupied(self):
        from orders.models import Order
        return Order.objects.filter(
            table=self,
            status__in=['pending', 'confirmed', 'preparing']
        ).exists()
