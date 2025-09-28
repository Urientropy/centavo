# finance/views.py

from rest_framework import filters
from .models import Income, Expense
from .serializers import IncomeSerializer, ExpenseSerializer
from inventory.views import BaseTenantViewSet  # Reutilizamos nuestro ViewSet base


class IncomeViewSet(BaseTenantViewSet):
    """
    ViewSet para el CRUD de Ingresos (Income), con seguridad multi-tenant.
    """
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']  # Orden por defecto


class ExpenseViewSet(BaseTenantViewSet):
    """
    ViewSet para el CRUD de Gastos (Expense), con seguridad multi-tenant.
    """
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']  # Orden por defecto