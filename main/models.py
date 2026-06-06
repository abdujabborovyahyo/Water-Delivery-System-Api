# main/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from users.models import Driver  # users ilovasidan haydovchini chaqiramiz


class Water(models.Model):
    """
    Sotiladigan suv mahsulotlari (brendlar) jadvali.
    """
    brand_name = models.CharField(max_length=100, db_index=True, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    liters = models.DecimalField(max_digits=5, decimal_places=2, help_text="Suv hajmi (litrda)")
    description = models.TextField(blank=True, null=True)

    is_available = models.BooleanField(default=True, help_text="Omborda bormi?")

    class Meta:
        ordering = ['brand_name']
        verbose_name = "Suv"
        verbose_name_plural = "Suvlar"

    def __str__(self):
        return f"{self.brand_name} ({self.liters}L) — {self.price} UZS"


class Customer(models.Model):
    """
    Buyurtma beruvchi mijozlar bazasi.
    """
    name = models.CharField(max_length=150, db_index=True)
    phone_number = models.CharField(max_length=20, unique=True, db_index=True)
    address = models.TextField()
    debt = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Mijozning kompaniyadan qarzi (agar bo'lsa)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"

    def __str__(self):
        return f"{self.name} | Tel: {self.phone_number}"


class Order(models.Model):
    """
    Tizimdagi barcha buyurtmalar va zanjirni bog'lovchi asosiy jadval.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Kutilmoqda'),
        ('DELIVERING', 'Yo\'lda / Yetkazilmoqda'),
        ('DELIVERED', 'Yetkazib berildi'),
        ('CANCELED', 'Bekor qilindi'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    water = models.ForeignKey(Water, on_delete=models.PROTECT, related_name='orders')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="Buyurtma qilingan suv soni")

    # Umumiy narx bazada saqlanadi (tarix uchun, agar suv narxi keyin o'zgarsa ham buyurtma narxi o'zgarmasligi kerak)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    # Kim qabul qildi va kim yetkazdi?
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                              related_name='accepted_orders')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, related_name='deliveries')

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"

    def save(self, *file, **kwargs):
        """
        Professional mantiq: Buyurtma saqlanishidan oldin, umumiy narxni
        suvning joriy narxini miqdoriga ko'paytirib, avtomatik hisoblaydi.
        """
        if not self.total_price:
            self.total_price = self.water.price * self.quantity
        super().save(*file, **kwargs)

    def __str__(self):
        return f"Buyurtma #{self.id} | {self.customer.name} | {self.total_price} UZS"
