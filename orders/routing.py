from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/orders/table/(?P<table_number>\w+)/$', consumers.OrderConsumer.as_asgi()),
    re_path(r'ws/orders/vendor/(?P<vendor_id>\w+)/$', consumers.VendorConsumer.as_asgi()),
    re_path(r'ws/orders/kitchen/$', consumers.KitchenConsumer.as_asgi()),
]
