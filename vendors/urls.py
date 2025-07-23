from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    # Vendor management URLs
    path('', views.vendor_list, name='vendor_list'),
    path('redirect/', views.vendor_redirect, name='vendor_redirect'),
    path('logout/', views.vendor_logout, name='vendor_logout'),
    path('<int:vendor_id>/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('<int:vendor_id>/debug/', views.debug_dashboard, name='debug_dashboard'),
    path('<int:vendor_id>/menu/', views.menu_management, name='menu_management'),

    # AJAX endpoints for vendor operations
    path('<int:vendor_id>/api/update-order-status/', views.update_order_status, name='update_order_status'),
    path('<int:vendor_id>/api/payment-report/', views.vendor_payment_report, name='vendor_payment_report'),
    path('<int:vendor_id>/api/toggle-menu-item/', views.toggle_menu_item, name='toggle_menu_item'),
]
