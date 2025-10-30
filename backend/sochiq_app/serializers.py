from rest_framework import serializers
from .models import Barber, Transaction, Inventory
from django.contrib.auth.models import User


class BarberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barber
        fields = '__all__'


class BarberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barber
        fields = ['name', 'telegram_id', 'phone_number', 'barbershop_name', 'towel_price']


class TransactionSerializer(serializers.ModelSerializer):
    barber_name = serializers.CharField(source='barber.name', read_only=True)
    admin_name = serializers.CharField(source='admin_user.username', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['barber', 'transaction_type', 'quantity', 'notes']
        extra_kwargs = {
            'barber': {'required': True},
            'transaction_type': {'required': True},
            'quantity': {'required': True}
        }


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'


class ReportSerializer(serializers.Serializer):
    period = serializers.CharField()
    given_towels = serializers.IntegerField()
    taken_towels = serializers.IntegerField()
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)