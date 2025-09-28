# users/serializers.py (Versión Definitiva)

from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from tenants.models import Tenant
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    # Declaramos los campos como en tu versión original.
    # La validación se hará en un método dedicado, no aquí.
    tenant_name = serializers.CharField(max_length=255, write_only=True, label="Nombre de la Empresa")
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    # El campo 'email' se hereda del modelo y su validador de unicidad se manejará abajo.

    class Meta:
        model = User
        fields = ('tenant_name', 'email', 'password', 'first_name', 'last_name')

    def validate_password(self, value):
        """
        Valida la fortaleza de la contraseña.
        """
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return value

    def validate(self, data):
        """
        Realiza validaciones de unicidad personalizadas para evitar el FieldError.
        Este método se ejecuta después de las validaciones de campo individuales.
        """
        # 1. Validar unicidad del email
        email_value = data['email']
        if User.objects.filter(email=email_value).exists():
            # El formato de la excepción es importante para que el frontend lo pueda leer.
            raise serializers.ValidationError({
                "email": "Ya existe un usuario registrado con esta dirección de correo electrónico."
            })

        # 2. Validar unicidad del nombre de la empresa (tenant_name)
        tenant_name_value = data['tenant_name']
        if Tenant.objects.filter(name=tenant_name_value).exists():
            raise serializers.ValidationError({
                "tenant_name": "Ya existe una empresa registrada con este nombre."
            })

        # Si todas las validaciones complejas pasan, devolvemos el diccionario de datos.
        return data

    def create(self, validated_data):
        """
        Crea el Tenant y el User de forma atómica.
        """
        try:
            with transaction.atomic():
                tenant = Tenant.objects.create(name=validated_data['tenant_name'])

                # Asumo que tu CustomUserManager (User.objects) acepta 'tenant' como un extra_field.
                # Si no, volvemos a la versión de dos pasos (crear y luego asignar).
                # Usamos el método .pop() para quitar tenant_name de los datos que se pasan a create_user,
                # ya que el modelo User no tiene ese campo.
                validated_data.pop('tenant_name')

                user = User.objects.create_user(
                    tenant=tenant,
                    **validated_data
                )

                return user
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Error en la creación: {str(e)}"})


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Sobrescribimos los campos para personalizar los mensajes de error
    # cuando los campos se envían vacíos.
    default_error_messages = {
        'no_active_account': 'No se encontró una cuenta activa con las credenciales proporcionadas.'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # // Personalizamos los mensajes de error para campos vacíos en español.
        self.fields[self.username_field].error_messages['required'] = 'Este campo es requerido.'
        self.fields[self.username_field].error_messages['blank'] = 'Este campo no puede estar en blanco.'
        self.fields['password'].error_messages['required'] = 'Este campo es requerido.'
        self.fields['password'].error_messages['blank'] = 'Este campo no puede estar en blanco.'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # El enriquecimiento del token se mantiene igual, es una buena práctica.
        token['first_name'] = user.first_name
        token['email'] = user.email
        return token

    def validate(self, attrs):
        # // El método validate es el corazón de la lógica de Simple JWT.
        # // Lo sobrescribimos para tener control total sobre la autenticación y los errores.

        # Primero, usamos la función de autenticación de Django.
        # attrs contiene {'email': '...', 'password': '...'}
        self.user = authenticate(
            request=self.context.get("request"),
            username=attrs.get(self.username_field),
            password=attrs.get("password")
        )

        if not self.user or not self.user.is_active:
            # // Si la autenticación falla, lanzamos una excepción de validación estándar de DRF.
            # // Esto generará una respuesta 401 Unauthorized (o 400 Bad Request dependiendo de la configuración del manejador de excepciones)
            # // con un mensaje claro y en español.
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        # Si la autenticación es exitosa, creamos los tokens.
        refresh = self.get_token(self.user)

        data = {}
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data

