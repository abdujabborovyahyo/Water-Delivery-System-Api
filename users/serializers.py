# users/serializers.py
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Driver

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    """Adminlar ro'yxatini chiqarish yoki ularni boshqarish uchun"""

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'birth_date']
        read_only_fields = ['id']

    def validate_birth_date(self, value):
        """
        Admin yoshini kunma-kun aniqlikda tekshirish (Kamida 19 yosh bo'lishi shart)
        """
        # birth_date ixtiyoriy maydon: qiymat berilmasa tekshiruvni o'tkazib yuboramiz
        if value is None:
            return value

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


class AdminRegistrationSerializer(serializers.ModelSerializer):
    """
    Yangi admin (user) yaratish uchun serializer.
    Parol va parol tasdiqini talab qiladi.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Kamida 8 ta belgidan iborat bo'lishi shart"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="Parolni tasdiqlang"
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone_number', 'birth_date', 'password', 'password_confirm'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'username': {
                'help_text': 'Faqat harf, raqam va @/./+/-/_ belgilari ruxsat',
            },
            'email': {
                'required': True,
                'help_text': 'Yaroqli email address kiritish shart'
            },
            'first_name': {
                'required': True,
            },
            'last_name': {
                'required': True,
            }
        }

    def validate_username(self, value):
        """Username unikali bo'lishini tekshirish"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu username allaqachon ro'yxatdan o'tgan.")
        return value

    def validate_email(self, value):
        """Email unikali bo'lishini tekshirish"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return value

    def validate_phone_number(self, value):
        """Phone number unikali bo'lishini tekshirish (agar berilsa)"""
        if value and User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Bu telefon raqami allaqachon ro'yxatdan o'tgan.")
        return value

    def validate_password(self, value):
        """Parol kuchini tekshirish (Django's validator orqali)"""
        try:
            validate_password(value)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate_birth_date(self, value):
        """
        Admin yoshini tekshirish (Kamida 19 yosh bo'lishi shart)
        """
        if value is None:
            return value

        today = timezone.now().date()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))

        if age < 19:
            raise serializers.ValidationError(
                "Admin sifatida ro'yxatdan o'tish uchun kamida 19 yosh bo'lishingiz shart."
            )

        if value > today:
            raise serializers.ValidationError("Tug'ilgan sana kelajakda bo'lishi mumkin emas.")

        return value

    def validate(self, data):
        """Parollar mos bo'lishini tekshirish"""
        password = data.get('password')
        password_confirm = data.pop('password_confirm', None)

        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": "Parollar mos kelmadi."
            })

        return data

    def create(self, validated_data):
        """Yangi admin user yaratish"""
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', ''),
            birth_date=validated_data.get('birth_date'),
            is_staff=True,  # Yangi admin sifatida yaratish
            is_active=True,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class DriverSerializer(serializers.ModelSerializer):
    """Haydovchilarni yaratish va ko'rish uchun serializer"""
    shift_display = serializers.CharField(source='get_shift_display', read_only=True)

    class Meta:
        model = Driver
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'shift', 'shift_display', 'is_active']
        read_only_fields = ['id']
