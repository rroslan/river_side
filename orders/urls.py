from django.urls import path
from . import views
from . import cashier_views

app_name = 'orders'

urlpatterns = [
    # Customer URLs
    path('', views.table_selection, name='table_selection'),
    path('search/', views.table_search, name='table_search'),

    path('table/<int:table_number>/', views.phone_input, name='phone_input'),
    path('table/<int:table_number>/menu/', views.table_menu, name='table_menu'),
    path('table/<int:table_number>/checkout/', views.checkout, name='checkout'),
    path('table/<int:table_number>/track/', views.track_orders, name='track_orders'),
    path('table/<int:table_number>/history/', views.order_history, name='order_history'),
    path('track/<int:table_number>/', views.track_orders, name='track_orders_short'),

    # Cashier URLs
    path('cashier/', cashier_views.cashier_dashboard, name='cashier_dashboard'),
    path('cashier/mark-paid/<uuid:order_id>/', cashier_views.mark_order_paid, name='mark_order_paid'),
    path('cashier/reset-table/<int:table_number>/', cashier_views.reset_table, name='reset_table'),
    path('cashier/order/<uuid:order_id>/', cashier_views.order_details, name='cashier_order_details'),
    path('cashier/tables-overview/', cashier_views.table_status_overview, name='table_status_overview'),
    path('cashier/sales-report/', cashier_views.daily_sales_report, name='daily_sales_report'),

    # WebSocket URL (handled by routing.py)
    # path('ws/orders/<int:table_number>/', ...),

    # API endpoints
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('api/update-cart-item/', views.update_cart_item, name='update_cart_item'),
    path('api/remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('api/place-order/<int:table_number>/', views.place_order, name='place_order'),
    path('api/cart-status/<int:table_number>/', views.get_cart_status, name='cart_status'),
    path('api/items-status/<int:table_number>/', views.get_table_items_status, name='table_items_status'),
    path('api/table-status/<int:table_number>/', views.table_status, name='table_status'),
    path('api/tables/', views.get_tables, name='get_tables'),
    path('api/status/', views.status_check, name='status_check'),
    path('api/clear-session/', views.clear_session, name='clear_session'),
    path('debug/cart/<int:table_number>/', views.debug_cart, name='debug_cart'),
]
