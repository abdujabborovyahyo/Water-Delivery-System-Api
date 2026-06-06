# Create your views here.

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Driver
from .serializers import AdminUserSerializer, DriverSerializer

User = get_user_model()

# =====================================================================
# 1. ADMIN API (Faqat List va Retrieve)
# =====================================================================
class AdminListGenericView(generics.ListAPIView):
    """Barcha adminlar ro'yxatini ko'rish"""
    permission_classes = [IsAuthenticated]
    queryset = User.objects.filter(is_staff=True) # Faqat admin huquqi borlarni chiqaradi
    serializer_class = AdminUserSerializer


class AdminDetailGenericView(generics.RetrieveAPIView):
    """Bitta admin ma'lumotlarini ID orqali ko'rish"""
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer


# =====================================================================
# 2. DRIVER API (Faqat List va Retrieve)
# =====================================================================
class DriverListGenericView(generics.ListAPIView):
    """Barcha haydovchilar ro'yxatini ko'rish"""
    permission_classes = [IsAuthenticated]
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer


class DriverDetailGenericView(generics.RetrieveAPIView):
    """Bitta haydovchini ID orqali ko'rish"""
    permission_classes = [IsAuthenticated]
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
