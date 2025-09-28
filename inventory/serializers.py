# inventory/serializers.py

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import RawMaterial, PurchaseBatch, Tenant  # Importamos Tenant para el PrimaryKeyRelatedField
from django.db.models import Sum
from django.utils.dateparse import parse_date
from datetime import datetime
from decimal import Decimal  # Importamos Decimal para el manejo preciso de números
import logging

logger = logging.getLogger(__name__)


class RawMaterialSerializer(serializers.ModelSerializer):
    # Campo calculado para el stock total
    total_stock = serializers.SerializerMethodField(read_only=True)

    # --- CAMPO TENANT PARA VALIDACIÓN DE UNICIDAD ---
    # Este campo es de escritura solamente, se espera en los datos de entrada
    # pero no se incluye en la salida JSON.
    tenant = serializers.PrimaryKeyRelatedField(
        queryset=Tenant.objects.all(),  # El queryset aquí puede ser amplio, la vista lo restringe.
        write_only=True,
        error_messages={'required': 'El ID de la empresa (tenant) es requerido para la validación.'}
        # Mensaje personalizado
    )

    # --- FIN CAMPO TENANT ---

    class Meta:
        model = RawMaterial
        # Asegúrate de que 'total_stock' y 'tenant' estén en los fields
        fields = ['id', 'tenant', 'name', 'unit_of_measure', 'description', 'created_at', 'total_stock']

        # Validador para asegurar que el nombre de la materia prima es único para un tenant dado.
        validators = [
            UniqueTogetherValidator(
                queryset=RawMaterial.objects.all(),
                fields=['tenant', 'name'],
                message="Ya existe una materia prima con este nombre en tu empresa."
            )
        ]

    def get_total_stock(self, obj):
        """
        Calcula el stock total sumando la CANTIDAD RESTANTE de todos los lotes asociados.
        """
        logger.info(f"Calculando total_stock para RawMaterial ID: {obj.id}")

        # --- INICIO DE LA CORRECCIÓN DEL BUG ---
        # ANTES (Incorrecto): Sumaba 'quantity', el total histórico de compras, no el stock real.
        # total = obj.batches.aggregate(total_quantity=Sum('quantity'))['total_quantity']
        #
        # AHORA (Correcto): Suma 'quantity_remaining', que es el stock real disponible.
        # Esto soluciona el bug de que el stock total no disminuía.
        total = obj.batches.aggregate(total_quantity=Sum('quantity_remaining'))['total_quantity']
        # --- FIN DE LA CORRECCIÓN DEL BUG ---

        # Nos aseguramos de devolver un Decimal para mantener la consistencia con el modelo.
        return total if total is not None else Decimal('0.00')


class PurchaseBatchSerializer(serializers.ModelSerializer):
    raw_material_name = serializers.CharField(source='raw_material.name', read_only=True)

    # --- CAMPO raw_material CON FILTRADO POR TENANT EN INIT ---
    raw_material = serializers.PrimaryKeyRelatedField(
        queryset=RawMaterial.objects.all(),  # Queryset inicial amplio, se filtra en __init__
        error_messages={'does_not_exist': 'La materia prima especificada no existe o no pertenece a tu empresa.'}
    )

    # --- FIN CAMPO raw_material ---

    class Meta:
        model = PurchaseBatch

        # --- INICIO DE LA CORRECCIÓN DEL BUG ---
        # ANTES (Incorrecto): El campo 'quantity_remaining' no estaba incluido en la lista.
        # Por esta razón, la API nunca devolvía el stock actualizado del lote.
        # fields = [
        #     'id', 'raw_material', 'raw_material_name', 'purchase_date',
        #     'quantity', 'total_cost', 'created_at'
        # ]
        #
        # AHORA (Correcto): Añadimos 'quantity_remaining'. Ahora la API expondrá
        # el stock real y restante de cada lote de compra.
        fields = [
            'id', 'raw_material', 'raw_material_name', 'purchase_date',
            'quantity', 'quantity_remaining', 'total_cost', 'created_at'
        ]
        # --- FIN DE LA CORRECCIÓN DEL BUG ---

    def __init__(self, *args, **kwargs):
        """
        Sobrescribimos el init para filtrar dinámicamente el queryset de raw_material
        basado en el tenant del usuario que realiza la petición.
        """
        super().__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request and hasattr(request, 'user') and hasattr(request.user, 'tenant'):
            tenant = request.user.tenant
            self.fields['raw_material'].queryset = RawMaterial.objects.filter(tenant=tenant)
        else:
            # Si no hay usuario/tenant válido, el queryset debe estar vacío
            # para prevenir que se seleccionen materias primas.
            self.fields['raw_material'].queryset = RawMaterial.objects.none()

    def validate(self, data):
        """
        Realiza la limpieza y validación de formatos para 'quantity', 'total_cost' y 'purchase_date'.
        """
        # 1. Limpiar y validar 'total_cost'
        if 'total_cost' in data and isinstance(data['total_cost'], str):
            cleaned_cost = data['total_cost'].replace('$', '').replace(',', '').strip()
            try:
                data['total_cost'] = float(cleaned_cost)  # Convertir a float para parseo preliminar
            except ValueError:
                raise serializers.ValidationError({"total_cost": "El costo total debe ser un número válido."})

        # 2. Limpiar y validar 'quantity'
        if 'quantity' in data and isinstance(data['quantity'], str):
            cleaned_quantity = data['quantity'].replace(',', '').strip()
            try:
                data['quantity'] = float(cleaned_quantity)
            except ValueError:
                raise serializers.ValidationError({"quantity": "La cantidad debe ser un número válido."})

        # 3. Limpiar y validar 'purchase_date'
        # El formato 'MM/DD/YYYY' del frontend es menos estándar para Django, lo parseamos manualmente.
        if 'purchase_date' in data and isinstance(data['purchase_date'], str):
            date_str = data['purchase_date']
            parsed_date = parse_date(date_str)  # Intenta parsear varios formatos
            if not parsed_date:
                # Si parse_date no lo pudo, intentamos un formato específico MM/DD/YYYY
                try:
                    parsed_date = datetime.strptime(date_str, '%m/%d/%Y').date()
                except ValueError:
                    raise serializers.ValidationError(
                        {"purchase_date": "El formato de fecha debe ser MM/DD/YYYY (ej. 09/21/2025)."})
            data['purchase_date'] = parsed_date

        # Llama a la validación original de ModelSerializer al final
        return super().validate(data)