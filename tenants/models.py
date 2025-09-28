from django.db import models

class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Nombre de la Empresa")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

