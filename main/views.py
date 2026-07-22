from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics, filters
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.pagination import PageNumberPagination

from core.permissions import IsAdmin, IsAdminOrReadOnly
from .models import Water, Customer, Order
from .serializers import (
    WaterSerializer, CustomerSerializer,
    OrderReadSerializer, OrderWriteSerializer
)


# =====================================================================
# 1. WATER APIVIEWS (Suv uchun CRUD)
# =====================================================================
class WaterListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

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
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

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
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

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
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

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
# 3. ORDER GENERICS (Buyurtma uchun List, Create, Retrieve, Update, Delete)
# =====================================================================
class OrderListCreateGenericView(generics.ListCreateAPIView):
    """
    Barcha buyurtmalarni ko'rish va yangi buyurtma yaratish.
    Faqat tizimga kirgan adminlar buyurtma yarata oladi.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Order.objects.all().select_related('customer', 'water', 'driver', 'admin')
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['-created_at', 'status']
    filterset_fields = ['customer', 'water', 'status', 'driver']
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        """Swagger va DRF POST paytida Write, GET paytida Read serializerini ko'rishi uchun"""
        if self.request.method == 'POST':
            return OrderWriteSerializer
        return OrderReadSerializer

    def perform_create(self, serializer):
        """Buyurtmani qabul qilgan admin sifatida tizimga kirgan user avtomat birikadi"""
        serializer.save(admin=self.request.user)

    @swagger_auto_schema(
        operation_description="Barcha buyurtmalar ro'yxatini olish. Filter qilinishi mumkin: customer, water, status, driver. Saralash: -created_at, status",
        responses={200: OrderReadSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Yangi buyurtma yaratish. Faqat admin huquqi borlarga ruxsat beriladi.",
        request_body=OrderWriteSerializer,
        responses={201: OrderReadSerializer(), 400: "Xato ma'lumot"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class OrderDetailGenericView(generics.RetrieveUpdateDestroyAPIView):
    """
    Bitta buyurtmani ko'rish, yangilash va o'chirish.
    Faqat admin huquqi borlarga ruxsat beriladi.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Order.objects.all().select_related('customer', 'water', 'driver', 'admin')

    def get_serializer_class(self):
        """GET uchun Read serializer, PUT/PATCH uchun Write serializer"""
        if self.request.method in ['PUT', 'PATCH']:
            return OrderWriteSerializer
        return OrderReadSerializer

    @swagger_auto_schema(
        operation_description="Buyurtma detaillarini ID orqali olish.",
        responses={200: OrderReadSerializer()}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Buyurtmani to'liq yangilash (PUT). Status va haydovchini o'zgartirish mumkin.",
        request_body=OrderWriteSerializer,
        responses={200: OrderReadSerializer(), 400: "Xato ma'lumot"}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Buyurtmani qisman yangilash (PATCH). Faqat kerakli maydonlarni o'zgartirib yuborish mumkin.",
        request_body=OrderWriteSerializer,
        responses={200: OrderReadSerializer(), 400: "Xato ma'lumot"}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Buyurtmani o'chirish (Faqat PENDING holatidagi buyurtmalarni o'chirish mumkin).",
        responses={204: "O'chirildi", 400: "O'chira olmadi"}
    )
    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status != 'PENDING':
            return Response(
                {
                    "error": "Faqat PENDING holatidagi buyurtmalarni o'chirish mumkin.",
                    "current_status": order.status
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().delete(request, *args, **kwargs)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
