# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

from tenants.models import Tenant
from .managers import CustomUserManager


class User(AbstractUser):
    # Heredamos de AbstractUser para obtener toda la funcionalidad de Django (login, permisos, etc.)
    # y añadimos nuestros campos personalizados.

    # Eliminamos el username y usaremos el email como identificador único.
    username = None
    email = models.EmailField('email address', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Campos requeridos al crear un superusuario

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="users", null=True, blank=True)
    objects = CustomUserManager()

    # // Usamos null=True, blank=True temporalmente. En un flujo de registro
    # // normal, el tenant siempre será creado y asignado. Esto nos da flexibilidad
    # // para la creación de superusuarios desde la consola que no están atados a un tenant.

    def __str__(self):
        return self.email
