from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Barber, Transaction, Inventory
from .serializers import *
from django.contrib.auth.models import User


class BarberViewSet(viewsets.ModelViewSet):
    queryset = Barber.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return BarberCreateSerializer
        return BarberSerializer

    @action(detail=True, methods=['post'])
    def update_towel_price(self, request, pk=None):
        barber = self.get_object()
        new_price = request.data.get('towel_price')

        if new_price is None:
            return Response(
                {'error': 'towel_price maydoni kerak'},
                status=status.HTTP_400_BAD_REQUEST
            )

        barber.towel_price = new_price
        barber.save()

        return Response(BarberSerializer(barber).data)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()

    def get_serializer_class(self):
        if self.action in ['create']:
            return TransactionCreateSerializer
        return TransactionSerializer

    def perform_create(self, serializer):
        try:
            # Ma'lumotlarni olish
            transaction_data = serializer.validated_data
            barber = transaction_data['barber']
            transaction_type = transaction_data['transaction_type']
            quantity = transaction_data['quantity']

            # Total_price ni hisoblash
            total_price = 0
            if transaction_type == 'taken':
                total_price = quantity * barber.towel_price

            # Transactionni saqlash
            transaction = serializer.save(
                admin_user=self.request.user,
                total_price=total_price
            )

            # Barber sochiq sonini yangilash
            if transaction_type == 'given':
                barber.towel_count += quantity
            else:  # taken
                barber.towel_count -= quantity

            barber.save()

            # Ombor holatini yangilash
            self.update_inventory(transaction)

        except Exception as e:
            print(f"Transaction yaratishda xato: {e}")
            raise

    def update_inventory(self, transaction):
        try:
            inventory, created = Inventory.objects.get_or_create(pk=1)

            if transaction.transaction_type == 'given':
                inventory.remaining_towels -= transaction.quantity
            else:  # taken
                inventory.remaining_towels += transaction.quantity

            inventory.save()
        except Exception as e:
            print(f"Ombor yangilashda xato: {e}")


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer

    @action(detail=False, methods=['post'])
    def initialize(self, request):
        total_towels = request.data.get('total_towels', 0)

        inventory, created = Inventory.objects.get_or_create(pk=1)
        inventory.total_towels = total_towels
        inventory.remaining_towels = total_towels
        inventory.save()

        return Response(InventorySerializer(inventory).data)


class ReportViewSet(viewsets.ViewSet):
    def list(self, request):
        period = request.query_params.get('period', 'today')

        # Vaqt oralig'ini aniqlash
        now = timezone.now()
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'week':
            start_date = now - timedelta(days=7)
            end_date = now
        elif period == 'month':
            start_date = now - timedelta(days=30)
            end_date = now
        elif period == 'all':
            start_date = None
            end_date = None
        else:
            return Response(
                {'error': 'Noto‘g‘ri period. today, week, month, all dan foydalaning'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filtrlash
        transactions = Transaction.objects.all()
        if start_date:
            transactions = transactions.filter(created_at__range=[start_date, end_date])

        # Hisobotni tayyorlash
        given_towels = transactions.filter(transaction_type='given').aggregate(
            total=Sum('quantity')
        )['total'] or 0

        taken_towels = transactions.filter(transaction_type='taken').aggregate(
            total=Sum('quantity')
        )['total'] or 0

        total_income = transactions.filter(transaction_type='taken').aggregate(
            total=Sum('total_price')
        )['total'] or 0

        report_data = {
            'period': period,
            'given_towels': given_towels,
            'taken_towels': taken_towels,
            'total_income': total_income,
            'start_date': start_date.date() if start_date else None,
            'end_date': end_date.date() if end_date else None,
        }

        serializer = ReportSerializer(report_data)
        return Response(serializer.data)