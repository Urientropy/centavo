# finance/models.py

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from tenants.models import Tenant

class Income(models.Model):
    """
    Representa un registro de ingreso manual para una empresa.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="incomes",
        verbose_name="Empresa"
    )
    description = models.CharField(max_length=255, verbose_name="Descripción")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Monto"
    )
    date = models.DateField(verbose_name="Fecha")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"

    def __str__(self):
        return f"Ingreso: {self.description} - ${self.amount} ({self.date.strftime('%Y-%m-%d')})"


class Expense(models.Model):
    """
    Representa un registro de gasto manual para una empresa.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name="Empresa"
    )
    description = models.CharField(max_length=255, verbose_name="Descripción")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Monto"
    )
    date = models.DateField(verbose_name="Fecha")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"

    def __str__(self):
        return f"Gasto: {self.description} - ${self.amount} ({self.date.strftime('%Y-%m-%d')})"