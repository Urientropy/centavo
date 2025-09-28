# inventory/models.py
from django.db import models
from tenants.models import Tenant


class RawMaterial(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="raw_materials")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    unit_of_measure = models.CharField(max_length=50, verbose_name="Unidad de Medida")
    description = models.TextField(blank=True, verbose_name="Descripción")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # // Aseguramos que el nombre de la materia prima sea único dentro de cada empresa.
        unique_together = ('tenant', 'name')
        verbose_name = "Materia Prima"
        verbose_name_plural = "Materias Primas"

    def __str__(self):
        return f"{self.name} ({self.unit_of_measure})"


class PurchaseBatch(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="purchase_batches")
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name="batches")
    purchase_date = models.DateField(verbose_name="Fecha de Compra")

    # // Usamos DecimalField para evitar errores de punto flotante en cálculos financieros y de inventario.
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo Total")

    # --- NUEVO CAMPO: quantity_remaining ---
    # Este campo es crucial para el seguimiento FIFO.
    # default=0.00 es una base segura, pero lo inicializaremos en migración.
    quantity_remaining = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Cantidad Restante",
        default=0.00  # Se actualizará en la migración a ser igual a 'quantity'
    )
    # --- FIN NUEVO CAMPO ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-purchase_date']
        verbose_name = "Lote de Compra"
        verbose_name_plural = "Lotes de Compra"

    # --- INICIO DE LA CORRECCIÓN DE INDENTACIÓN ---
    # El método 'save' debe estar aquí, al mismo nivel que '__str__' y 'Meta'.
    def save(self, *args, **kwargs):
        # Si el objeto es nuevo (no tiene pk), inicializamos quantity_remaining.
        if not self.pk:
            self.quantity_remaining = self.quantity
        super().save(*args, **kwargs)  # Llama al método save original
    # --- FIN DE LA CORRECCIÓN DE INDENTACIÓN ---


    def __str__(self):
        return f"Lote de {self.raw_material.name} - {self.purchase_date} ({self.quantity_remaining}/{self.quantity})"