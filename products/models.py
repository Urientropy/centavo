# products/models.py

from django.db import models
from tenants.models import Tenant
from inventory.models import RawMaterial # Importación confirmada

class Product(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255, verbose_name="Nombre del Producto")
    category = models.CharField(max_length=100, blank=True, verbose_name="Categoría")
    description = models.TextField(blank=True, verbose_name="Descripción")
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Precio de Venta Sugerido"
    )
    stock = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Stock Disponible"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('tenant', 'name')
        ordering = ['name']
        verbose_name = "Producto Terminado"
        verbose_name_plural = "Productos Terminados"

    def __str__(self):
        return self.name

# --- NUEVO MODELO PARA HU-05 ---
class RecipeIngredient(models.Model):
    """
    Representa un ingrediente en la receta de un Producto Terminado.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Producto Terminado"
    )
    raw_material = models.ForeignKey(
        RawMaterial,
        on_delete=models.PROTECT, # Seguridad: No permitir borrar una materia prima si está en una receta
        related_name="product_recipes",
        verbose_name="Materia Prima"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Cantidad Requerida"
    )

    class Meta:
        unique_together = ('product', 'raw_material')
        verbose_name = "Ingrediente de Receta"
        verbose_name_plural = "Ingredientes de Receta"

    def __str__(self):
        return f"{self.quantity} de {self.raw_material.name} para {self.product.name}"
