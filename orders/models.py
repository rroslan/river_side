from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from vendors.models import MenuItem, Table, Vendor
import uuid

class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    PREPARING = 'preparing', 'Preparing'
    READY = 'ready', 'Ready'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=100, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    estimated_ready_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{str(self.id)[:8]} - Table {self.table.number}"

    def calculate_total(self):
        """Calculate total amount from order items"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        return total

    def get_vendors(self):
        """Get all vendors involved in this order"""
        from vendors.models import Vendor
        vendor_ids = set()
        for item in self.items.all():
            vendor_ids.add(item.menu_item.category.vendor.id)
        return Vendor.objects.filter(id__in=vendor_ids)

    def get_preparation_time(self):
        """Get estimated preparation time based on longest item prep time"""
        max_prep_time = self.items.aggregate(
            models.Max('menu_item__preparation_time')
        )['menu_item__preparation_time__max']
        return max_prep_time or 15

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    def save(self, *args, **kwargs):
        # Set unit price from menu item if not set
        if not self.unit_price:
            self.unit_price = self.menu_item.price

        # Calculate subtotal
        self.subtotal = self.unit_price * self.quantity

        super().save(*args, **kwargs)

        # Update order total
        self.order.calculate_total()
        self.order.save()

    @property
    def vendor(self):
        return self.menu_item.vendor

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=OrderStatus.choices)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Order Status Histories'

    def __str__(self):
        return f"Order {self.order.id} - {self.get_status_display()} at {self.timestamp}"

class Cart(models.Model):
    """Temporary cart for customers before placing order"""
    session_key = models.CharField(max_length=40, unique=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        table_info = f"Table {self.table.number}" if self.table else "No table"
        return f"Cart - {table_info}"

    def get_total(self):
        return sum(item.subtotal for item in self.items.all())

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'menu_item']

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.menu_item.price
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
