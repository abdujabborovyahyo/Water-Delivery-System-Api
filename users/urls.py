from django.urls import path
from .views import (
    AdminListGenericView, AdminDetailGenericView,
    DriverListGenericView, DriverDetailGenericView
)

from rest_framework_simplejwt.views import token_obtain_pair, token_refresh

urlpatterns = [
    # Adminlar uchun URL-lar
    path('admins/', AdminListGenericView.as_view(), name='admin-list'),
    path('admins/<int:pk>/', AdminDetailGenericView.as_view(), name='admin-detail'),

    # Haydovchilar uchun URL-lar
    path('drivers/', DriverListGenericView.as_view(), name='driver-list'),
    path('drivers/<int:pk>/', DriverDetailGenericView.as_view(), name='driver-detail'),

    path('token/', token_obtain_pair),

    path('token/refresh/', token_refresh),
]
