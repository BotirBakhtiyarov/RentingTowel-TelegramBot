from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BarberViewSet, TransactionViewSet, InventoryViewSet, ReportViewSet

router = DefaultRouter()
router.register(r'barbers', BarberViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'reports', ReportViewSet, basename='reports')

urlpatterns = [
    path('api/', include(router.urls)),
]