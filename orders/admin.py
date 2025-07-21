from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem, OrderStatusHistory, Cart, CartItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id_short', 'table', 'customer_name', 'status', 'total_amount', 'created_at', 'vendor_list')
    list_filter = ('status', 'created_at', 'table__number')
    search_fields = ('id', 'customer_name', 'customer_phone', 'table__number')
    readonly_fields = ('id', 'created_at', 'updated_at', 'total_amount')
    list_editable = ('status',)
    ordering = ('-created_at',)

    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'table', 'status', 'total_amount')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_phone')
        }),
        ('Order Details', {
            'fields': ('notes', 'estimated_ready_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'ready_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )

    def order_id_short(self, obj):
        return str(obj.id)[:8]
    order_id_short.short_description = 'Order ID'

    def vendor_list(self, obj):
        vendors = obj.get_vendors()
        if vendors:
            return ', '.join([vendor.name for vendor in vendors])
        return 'No vendors'
    vendor_list.short_description = 'Vendors'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('menu_item', 'quantity', 'unit_price', 'subtotal', 'special_instructions', 'status')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'unit_price', 'subtotal', 'status')
    list_filter = ('status', 'menu_item__category__vendor', 'created_at')
    search_fields = ('order__id', 'menu_item__name', 'menu_item__category__vendor__name')
    readonly_fields = ('subtotal', 'created_at', 'updated_at')

    fieldsets = (
        ('Item Information', {
            'fields': ('order', 'menu_item', 'quantity', 'unit_price', 'subtotal')
        }),
        ('Details', {
            'fields': ('special_instructions', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'changed_by', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('order__id', 'changed_by__username')
    readonly_fields = ('timestamp',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'table', 'item_count', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('created_at', 'table__number')
    search_fields = ('session_key', 'table__number')
    readonly_fields = ('created_at', 'updated_at', 'item_count', 'total_amount')

    def cart_id(self, obj):
        return obj.session_key[:10] + '...' if len(obj.session_key) > 10 else obj.session_key
    cart_id.short_description = 'Cart ID'

    def item_count(self, obj):
        return obj.get_item_count()
    item_count.short_description = 'Items'

    def total_amount(self, obj):
        return f"${obj.get_total():.2f}"
    total_amount.short_description = 'Total'

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'menu_item', 'quantity', 'unit_price', 'subtotal', 'created_at')
    list_filter = ('menu_item__category__vendor', 'created_at')
    search_fields = ('cart__session_key', 'menu_item__name')
    readonly_fields = ('subtotal', 'created_at')

    fieldsets = (
        ('Item Information', {
            'fields': ('cart', 'menu_item', 'quantity', 'unit_price', 'subtotal')
        }),
        ('Details', {
            'fields': ('special_instructions',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )

# Add inlines to the main models
OrderAdmin.inlines = [OrderItemInline]
CartAdmin.inlines = [CartItemInline]
