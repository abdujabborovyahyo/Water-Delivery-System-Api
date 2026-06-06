# users/serializers.py
from django.utils import timezone

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Driver

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    """Adminlar ro'yxatini chiqarish yoki ularni boshqarish uchun"""

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number']
        read_only_fields = ['id']

    def validate_birth_date(self, value):
        """
        Admin yoshini kunma-kun aniqlikda tekshirish (Kamida 19 yosh bo'lishi shart)
        """
        today = timezone.now().date()

        # Yoshni aniq hisoblash formulasi (oy va kunni inobatga olgan holda)
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))

        if age < 19:
            raise serializers.ValidationError(
                "Kechirasiz, admin sifatida ro'yxatdan o'tish uchun yoshingiz mos kelmaydi. Kamida 19 yosh bo'lishingiz shart.")

        # Agar kelajakdagi sanani yuborsa (masalan, 2030-yil)
        if value > today:
            raise serializers.ValidationError("Tug'ilgan sana kelajakda bo'lishi mumkin emas.")

        return value


class DriverSerializer(serializers.ModelSerializer):
    """Haydovchilarni yaratish va ko'rish uchun serializer"""
    shift_display = serializers.CharField(source='get_shift_display', read_only=True)

    class Meta:
        model = Driver
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'shift', 'shift_display', 'is_active']
        read_only_fields = ['id']
