# finance/serializers.py

from rest_framework import serializers
from .models import Income, Expense
from tenants.models import Tenant

class IncomeSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Income.
    """
    tenant = serializers.PrimaryKeyRelatedField(
        queryset=Tenant.objects.all(),
        write_only=True,
        required=False  # Inyectado desde la vista
    )

    class Meta:
        model = Income
        fields = ['id', 'tenant', 'description', 'amount', 'date', 'created_at']
        # La validación UniqueTogether no es necesaria aquí.

    def create(self, validated_data):
        # Aseguramos que el tenant se inyecte en el momento de la creación
        tenant = self.context['request'].user.tenant
        validated_data['tenant'] = tenant
        return super().create(validated_data)


class ExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Expense.
    """
    tenant = serializers.PrimaryKeyRelatedField(
        queryset=Tenant.objects.all(),
        write_only=True,
        required=False  # Inyectado desde la vista
    )

    class Meta:
        model = Expense
        fields = ['id', 'tenant', 'description', 'amount', 'date', 'created_at']

    def create(self, validated_data):
        # Aseguramos que el tenant se inyecte en el momento de la creación
        tenant = self.context['request'].user.tenant
        validated_data['tenant'] = tenant
        return super().create(validated_data)