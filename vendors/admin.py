from django.contrib import admin
from .models import Vendor, Category, MenuItem, Table

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor_type', 'is_active', 'owner', 'opening_time', 'closing_time')
    list_filter = ('vendor_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'vendor_type', 'description', 'owner')
        }),
        ('Settings', {
            'fields': ('is_active', 'opening_time', 'closing_time', 'logo')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'is_active', 'sort_order')
    list_filter = ('vendor', 'is_active')
    search_fields = ('name', 'description', 'vendor__name')
    list_editable = ('sort_order', 'is_active')
    ordering = ('vendor', 'sort_order', 'name')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'vendor_name', 'price', 'is_available', 'preparation_time')
    list_filter = ('category__vendor', 'category', 'is_available', 'is_spicy', 'is_vegetarian', 'is_vegan')
    search_fields = ('name', 'description', 'ingredients', 'category__name', 'category__vendor__name')
    list_editable = ('price', 'is_available', 'preparation_time')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'price')
        }),
        ('Availability', {
            'fields': ('is_available', 'preparation_time')
        }),
        ('Details', {
            'fields': ('ingredients', 'calories', 'image')
        }),
        ('Dietary Options', {
            'fields': ('is_spicy', 'is_vegetarian', 'is_vegan')
        }),
        ('Display', {
            'fields': ('sort_order',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def vendor_name(self, obj):
        return obj.category.vendor.name if obj.category and obj.category.vendor else 'No Vendor'
    vendor_name.short_description = 'Vendor'
    vendor_name.admin_order_field = 'category__vendor__name'

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'seats', 'is_active', 'is_occupied', 'created_at')
    list_filter = ('is_active', 'seats')
    search_fields = ('number',)
    list_editable = ('seats', 'is_active')
    readonly_fields = ('created_at', 'is_occupied')

    def is_occupied(self, obj):
        return obj.is_occupied
    is_occupied.boolean = True
    is_occupied.short_description = 'Currently Occupied'
