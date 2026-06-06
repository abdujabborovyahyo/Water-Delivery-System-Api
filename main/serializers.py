# main/serializers.py
from rest_framework import serializers
from .models import Water, Customer, Order
from users.serializers import DriverSerializer, AdminUserSerializer

# =====================================================================
# WATER & CUSTOMER SERIALIZERS
# =====================================================================
class WaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water
        fields = ['id', 'brand_name', 'price', 'liters', 'description', 'is_available']
        read_only_fields = ['id']

    def validate_liters(self, value):
        if value.liters > 19:
            raise serializers.ValidationError("Bunday katta litrlarda suv sotilmaydi")
        return value


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone_number', 'address', 'debt', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_debt(self, value):
        """Mijozning boshlang'ich qarzi manfiy bo'lmasligini tekshirish"""
        if value < 0:
            raise serializers.ValidationError("Mijozning qarzi noldan kam bo'lishi mumkin emas.")
        return value


# =====================================================================
# ORDER SERIALIZERS (Professional tarzda Read va Write-ga ajratilgan)
# =====================================================================
class OrderReadSerializer(serializers.ModelSerializer):
    """
    Dashboard yoki API-da buyurtmalarni barcha bog'liqliklari (Mijoz kim, qaysi suv,
    qaysi haydovchi) bilan nested (to'liq) holatda chiroyli ko'rsatish uchun (GET).
    """
    customer = CustomerSerializer(read_only=True)
    water = WaterSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)
    admin = AdminUserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'water', 'quantity', 'total_price',
            'admin', 'driver', 'status', 'status_display', 'created_at', 'updated_at'
        ]


class OrderWriteSerializer(serializers.ModelSerializer):
    """
    Yangi buyurtma olish yoki uni tahrirlash uchun (POST/PUT/PATCH).
    Bu yerda xavfsizlik va biznes-logika qat'iy tekshiriladi.
    """
    # admin va total_price avtomatik sozlanganligi uchun ularni read_only qilamiz
    admin = serializers.PrimaryKeyRelatedField(read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'water', 'quantity', 'total_price', 'admin', 'driver', 'status']

    def validate_water(self, value):
        """Biznes-logika: Tanlangan suv brendi omborda (is_available=True) ekanligini tekshirish"""
        if not value.is_available:
            raise serializers.ValidationError(f"Kechirasiz, '{value.brand_name}' suv brendi ayni damda omborda mavjud emas.")
        return value

    def validate_driver(self, value):
        """Biznes-logika: Tanlangan haydovchi faol (is_active=True) ekanligini tekshirish"""
        if value and not value.is_active:
            raise serializers.ValidationError(f"Haydovchi '{value.first_name}' hozirda faol emas (ta'tilda yoki bo'shatilgan).")
        return value

    def validate_customer(self, value):
        if value.debt > 500000:
            raise serializers.ValidationError(f"Qarzingiz juda ko’p, buyurtma qilolmaysiz!")
        return value

    def validate(self, attrs):
        """Umumiy mantiqiy tekshiruvlar uchun validation"""
        # Masalan, agar status 'DELIVERING' (Yo'lda) qilib o'zgartirilsa, haydovchi biriktirilgan bo'lishi shart!
        status = attrs.get('status', self.instance.status if self.instance else 'PENDING')
        driver = attrs.get('driver', self.instance.driver if self.instance else None)

        if status == 'DELIVERING' and not driver:
            raise serializers.ValidationError({
                "driver": "Buyurtmani yetkazilmoqda statusiga o'tkazishdan oldin haydovchini biriktirishingiz shart!"
            })
        return attrs
