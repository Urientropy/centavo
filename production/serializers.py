# production/serializers.py

from rest_framework import serializers
from .models import ProductionLog
from products.models import Product

class ProductionRegistrationSerializer(serializers.Serializer):
    """
    Serializer para validar los datos de entrada al registrar una producción.
    Este serializer no está asociado a un modelo, solo valida el payload de entrada.
    """
    product_id = serializers.IntegerField(
        required=True,
        help_text="ID del Producto Terminado que se va a producir."
    )
    quantity_produced = serializers.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        min_value=0.01, # No se puede producir una cantidad cero o negativa.
        help_text="Cantidad de unidades del producto que se han fabricado."
    )

    def validate_product_id(self, value):
        """
        Valida que el producto exista y pertenezca al tenant del usuario.
        """
        tenant = self.context['request'].user.tenant
        if not Product.objects.filter(id=value, tenant=tenant).exists():
            raise serializers.ValidationError("Producto no encontrado o no pertenece a tu empresa.")
        return value


class ProductionLogSerializer(serializers.ModelSerializer):
    """
    Serializer para la lectura de los registros de producción.
    Proporciona una representación detallada del evento de producción.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductionLog
        fields = [
            'id',
            'product',
            'product_name',
            'quantity_produced',
            'total_cost',
            'production_date'
        ]
        read_only_fields = fields # Este serializer es solo para lectura