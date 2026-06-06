# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Tizim Adminlari uchun AbstractUser modeli.
    Kelajakda rasm, lavozim kabi qo'shimcha maydonlar qo'shish mumkin.
    """
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Adminlar"

    def __str__(self):
        return f"Admin: {self.username} ({self.get_full_name()})"


class Driver(models.Model):
    """
    Buyurtmalarni yetkazib beruvchi haydovchilar modeli.
    """
    SHIFT_CHOICES = [
        ('MORNING', 'Ertalabki smena (08:00 - 14:00)'),
        ('EVENING', 'Kechki smena (14:00 - 20:00)'),
        ('FULL_DAY', 'To\'liq kun (08:00 - 20:00)'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True, db_index=True)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='FULL_DAY')
    is_active = models.BooleanField(default=True, help_text="Haydovchi hozirda ishlayaptimi?")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = "Haydovchi"
        verbose_name_plural = "Haydovchilar"

    def __str__(self):
        return f"{self.first_name} {self.last_name} | {self.get_shift_display()}"
