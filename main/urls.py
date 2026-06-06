from django.urls import path
from .views import (
    WaterListCreateAPIView, WaterDetailAPIView,
    CustomerListCreateAPIView, CustomerDetailAPIView,
    OrderListCreateGenericView
)

urlpatterns = [
    # Suv (Water) uchun URL-lar
    path('waters/', WaterListCreateAPIView.as_view(), name='water-list-create'),
    path('waters/<int:pk>/', WaterDetailAPIView.as_view(), name='water-detail'),

    # Mijoz (Customer) uchun URL-lar
    path('customers/', CustomerListCreateAPIView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerDetailAPIView.as_view(), name='customer-detail'),

    # Buyurtma (Order) uchun URL-lar
    path('orders/', OrderListCreateGenericView.as_view(), name='order-list-create'),
]
