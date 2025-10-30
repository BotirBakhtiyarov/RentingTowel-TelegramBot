from django.db import models
from django.contrib.auth.models import User

class Barber(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ismi")
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon raqami")
    barbershop_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Sartaroshxona nomi")
    towel_count = models.IntegerField(default=0, verbose_name="Sochiqlar soni")
    towel_price = models.DecimalField(max_digits=10, decimal_places=2, default=2000, verbose_name="Sochiq narxi")  # Default 2000 so'm
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sartarosh"
        verbose_name_plural = "Sartaroshlar"

    def __str__(self):
        return f"{self.name} ({self.telegram_id})"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('given', 'Berildi'),
        ('taken', 'Olingan'),
    )

    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, verbose_name="Sartarosh")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name="Turi")
    quantity = models.IntegerField(verbose_name="Miqdor")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Jami narx")  # default qo'shildi
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Admin")
    notes = models.TextField(blank=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tranzaksiya"
        verbose_name_plural = "Tranzaksiyalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.barber.name} - {self.get_transaction_type_display()} - {self.quantity}"

    def save(self, *args, **kwargs):
        # Agar total_price hisoblanmagan bo'lsa, hisoblaymiz
        if not self.total_price and self.transaction_type == 'taken':
            self.total_price = self.quantity * self.barber.towel_price
        super().save(*args, **kwargs)

class Inventory(models.Model):
    total_towels = models.IntegerField(default=0, verbose_name="Jami sochiqlar")
    remaining_towels = models.IntegerField(default=0, verbose_name="Qolgan sochiqlar")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Oxirgi yangilanish")

    class Meta:
        verbose_name = "Ombor"
        verbose_name_plural = "Ombor"

    def __str__(self):
        return f"Ombor: {self.remaining_towels}/{self.total_towels}"