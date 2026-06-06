from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics, filters
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.pagination import PageNumberPagination

from .models import Water, Customer, Order
from .serializers import (
    WaterSerializer, CustomerSerializer,
    OrderReadSerializer, OrderWriteSerializer
)


# =====================================================================
# 1. WATER APIVIEWS (Suv uchun CRUD)
# =====================================================================
class WaterListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 1. GET so'rovini Swaggerda chiroyli ko'rsatish
    @swagger_auto_schema(
        operation_description="Barcha ombordagi suv brendlari ro'yxatini olish.",
        responses={200: WaterSerializer(many=True)}
    )
    def get(self, request):
        water = Water.objects.all()
        serializer = WaterSerializer(water, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. POST so'rovida qanday ma'lumot kiritish kerakligini Swaggerga o'rgatish
    @swagger_auto_schema(
        operation_description="Yangi suv brendi qo'shish (Faqat adminlar uchun).",
        request_body=WaterSerializer, # Swagger shu serializerga qarab forma ochadi
        responses={201: WaterSerializer(), 400: "Xato ma'lumot kiritildi"}
    )
    def post(self, request):
        serializer = WaterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WaterDetailAPIView(APIView):
    """Bitta suvni ko'rish (GET), yangilash (PUT/PATCH) va o'chirish (DELETE)"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        water = get_object_or_404(Water, pk=pk)
        serializer = WaterSerializer(water)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        water = get_object_or_404(Water, pk=pk)
        serializer = WaterSerializer(water, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        water = get_object_or_404(Water, pk=pk)
        serializer = WaterSerializer(water, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        water = get_object_or_404(Water, pk=pk)
        water.delete()
        return Response(
            {"success": True, "message": "Suv muvaffaqiyatli o'chirildi."},
            status=status.HTTP_204_NO_CONTENT
        )


# =====================================================================
# 2. CUSTOMER APIVIEWS (Mijoz uchun CRUD)
# =====================================================================
class CustomerListCreateAPIView(APIView):
    """Mijozlar ro'yxati (GET) va yangi mijoz qo'shish (POST)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomerDetailAPIView(APIView):
    """Mijozni ko'rish (GET), yangilash (PUT/PATCH) va o'chirish (DELETE)"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()
        return Response(
            {"success": True, "message": "Mijoz o'chirildi."},
            status=status.HTTP_204_NO_CONTENT
        )


# =====================================================================
# 3. ORDER GENERICS (Buyurtma uchun faqat List va Post)
# =====================================================================
class OrderListCreateGenericView(generics.ListCreateAPIView):
    """
    Shartga ko'ra faqat list va post amallari uchun.
    Generics yordamida juda qisqa va mukammal yoziladi.
    """
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['-created_at']
    filterset_fields = ['customer', 'water']

    def get_serializer_class(self):
        """Swagger va DRF POST paytida Write, GET paytida Read serializerini ko'rishi uchun"""
        if self.request.method == 'POST':
            return OrderWriteSerializer
        return OrderReadSerializer

    def perform_create(self, serializer):
        """Buyurtmani qabul qilgan admin sifatida tizimga kirgan user avtomat birikadi"""
        serializer.save(admin=self.request.user)


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100
