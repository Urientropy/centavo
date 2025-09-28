# production/models.py

from django.db import models
from django.conf import settings
from tenants.models import Tenant
from products.models import Product

class ProductionLog(models.Model):
    """
    Registra un lote de producción de un producto terminado.
    Este modelo es el resultado de una operación exitosa de producción.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="production_logs",
        verbose_name="Empresa"
    )
    product = models.ForeignKey(
        Product,
        # PRINCIPIO: No permitir eliminar un producto si tiene historial de producción.
        # Esto es crucial para la integridad de los datos históricos y contables.
        on_delete=models.PROTECT,
        related_name="production_logs",
        verbose_name="Producto Terminado"
    )
    quantity_produced = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Cantidad Producida"
    )
    # // Este costo se calcula en el momento de la producción basado en los
    # // costos reales de los lotes de materia prima consumidos (FIFO).
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Costo Total de Producción"
    )
    production_date = models.DateTimeField(
        auto_now_add=True, # La producción se registra en el momento de la llamada a la API.
        verbose_name="Fecha de Producción"
    )

    class Meta:
        ordering = ['-production_date']
        verbose_name = "Registro de Producción"
        verbose_name_plural = "Registros de Producción"

    def __str__(self):
        return f"Producción de {self.quantity_produced} x {self.product.name} el {self.production_date.strftime('%Y-%m-%d')}"
