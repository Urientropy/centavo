# production/services.py

from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404

from products.models import Product
from inventory.models import PurchaseBatch
from .models import ProductionLog


class InsufficientStockError(Exception):
    """Excepción personalizada para manejar fallos por falta de stock de forma controlada."""

    def __init__(self, message, details):
        super().__init__(message)
        self.details = details


@transaction.atomic
def register_production_batch(user, product_id, quantity_to_produce: Decimal):
    """
    Servicio principal para registrar un lote de producción. Es una operación atómica.

    1. Valida que el producto y su receta existan.
    2. Calcula las materias primas totales necesarias.
    3. Bloquea las filas de los lotes de compra para evitar race conditions.
    4. Verifica si hay stock suficiente para CADA materia prima.
    5. Si hay stock, descuenta las cantidades de los lotes (FIFO) y calcula el costo.
    6. Si todo tiene éxito, incrementa el stock del producto y crea el registro de producción.
    7. Si falla en cualquier punto, toda la transacción se revierte.

    :param user: El usuario que realiza la operación (para obtener el tenant).
    :param product_id: ID del producto a fabricar.
    :param quantity_to_produce: Cantidad (Decimal) del producto a fabricar.
    :return: La instancia del ProductionLog creado.
    :raises ValueError: Si el producto no tiene receta.
    :raises InsufficientStockError: Si no hay suficiente stock de alguna materia prima.
    """
    tenant = user.tenant
    product = get_object_or_404(Product.objects.select_related('tenant'), id=product_id, tenant=tenant)
    recipe_ingredients = product.recipe_ingredients.select_related('raw_material').all()

    if not recipe_ingredients.exists():
        raise ValueError(f"El producto '{product.name}' no tiene una receta definida y no puede ser producido.")

    # 1. Calcular los requerimientos totales de materias primas
    required_materials = {}
    for item in recipe_ingredients:
        required_materials[item.raw_material.id] = {
            'raw_material': item.raw_material,
            'quantity_needed': item.quantity * quantity_to_produce
        }

    total_production_cost = Decimal('0.0')

    # 2. Verificar stock y descontar para cada materia prima
    for rm_id, requirement in required_materials.items():
        raw_material = requirement['raw_material']
        quantity_needed = requirement['quantity_needed']

        # **CRÍTICO**: Bloqueamos los lotes relevantes para esta transacción.
        # Esto previene que otra petición simultánea modifique el stock mientras calculamos.
        available_batches = PurchaseBatch.objects.select_for_update().filter(
            tenant=tenant,
            raw_material=raw_material,
            quantity_remaining__gt=0
        ).order_by('purchase_date')  # Orden FIFO

        total_available = sum(batch.quantity_remaining for batch in available_batches)

        if total_available < quantity_needed:
            # Lanzamos la excepción con los detalles para la respuesta de la API
            raise InsufficientStockError(
                message=f"Stock insuficiente para '{raw_material.name}'.",
                details={
                    "error_code": "INSUFFICIENT_STOCK",
                    "detail": f"No hay suficiente stock para la materia prima '{raw_material.name}'.",
                    "missing_raw_material": {"id": raw_material.id, "name": raw_material.name},
                    "quantity_required": f"{quantity_needed:.2f}",
                    "quantity_available": f"{total_available:.2f}"
                }
            )

        # 3. Lógica de descuento FIFO y cálculo de costos
        cost_for_this_material = Decimal('0.0')
        remaining_to_deduct = quantity_needed
        for batch in available_batches:
            if remaining_to_deduct <= 0:
                break

            cost_per_unit = batch.total_cost / batch.quantity if batch.quantity > 0 else Decimal('0.0')

            amount_to_take = min(remaining_to_deduct, batch.quantity_remaining)

            batch.quantity_remaining -= amount_to_take
            cost_for_this_material += amount_to_take * cost_per_unit
            remaining_to_deduct -= amount_to_take

            batch.save()

        total_production_cost += cost_for_this_material

    # 4. Finalizar la producción si todo fue exitoso
    product.stock += quantity_to_produce
    product.save()

    production_log = ProductionLog.objects.create(
        tenant=tenant,
        product=product,
        quantity_produced=quantity_to_produce,
        total_cost=total_production_cost.quantize(Decimal('0.01'))
    )

    return production_log