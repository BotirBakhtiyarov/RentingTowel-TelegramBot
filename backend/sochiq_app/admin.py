from django.contrib import admin
from .models import Barber, Transaction, Inventory

@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ['name', 'telegram_id', 'towel_count', 'towel_price', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'telegram_id']
    list_editable = ['towel_price', 'is_active']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['barber', 'transaction_type', 'quantity', 'total_price', 'admin_user', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['barber__name', 'notes']
    readonly_fields = ['created_at']

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['total_towels', 'remaining_towels', 'last_updated']
    readonly_fields = ['last_updated']