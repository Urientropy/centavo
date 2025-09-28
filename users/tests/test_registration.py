# Fichero: users/tests/test_registration.py
# Test Suite para la Historia de Usuario HU-01: Registro de Nuevo Productor (VERSIÓN CORREGIDA PARA i18n - Español)

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from users.models import User
from tenants.models import Tenant


class RegisterUserAPITests(APITestCase):
    """
    Pruebas que cubren el flujo completo de registro de un nuevo productor
    y su empresa (tenant), especificado en la HU-01.
    """

    def setUp(self):
        self.register_url = reverse('auth_register')
        self.valid_payload = {
            'tenant_name': 'Mi Finca Cafetera',
            'email': 'productor@cafetera.com',
            'password': 'SuperSecretPassword123!',
            'first_name': 'Juan',
            'last_name': 'Valdez'
        }

    def test_successful_registration_creates_user_and_tenant_and_returns_tokens(self):
        # ... (Esta prueba no necesita cambios)
        # Arrange
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Tenant.objects.count(), 0)

        # Act
        response = self.client.post(self.register_url, self.valid_payload, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"La API devolvió un error: {response.data}")
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], self.valid_payload['email'])
        self.assertNotIn('password', response.data['user'])
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Tenant.objects.count(), 1)

        created_user = User.objects.get(email=self.valid_payload['email'])
        created_tenant = Tenant.objects.get(name=self.valid_payload['tenant_name'])

        self.assertEqual(created_user.tenant, created_tenant)
        self.assertTrue(created_user.check_password(self.valid_payload['password']))

    def test_register_with_existing_email_fails_and_is_atomic(self):
        # ...
        # Arrange
        initial_tenant = Tenant.objects.create(name="Finca Original")
        User.objects.create_user(
            email=self.valid_payload['email'],
            password='password123',
            tenant=initial_tenant,
            first_name='Original',
            last_name='User'
        )
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Tenant.objects.count(), 1)

        # Act
        response = self.client.post(self.register_url, self.valid_payload, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        # --- CORRECCIÓN i18n ---
        self.assertEqual(str(response.data['email'][0]), 'Ya existe usuario con este email address.')
        self.assertEqual(Tenant.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)

    def test_register_with_missing_required_field_fails(self):
        # ...
        # Arrange
        payload_without_email = self.valid_payload.copy()
        del payload_without_email['email']

        # Act
        response = self.client.post(self.register_url, payload_without_email, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        # --- CORRECCIÓN i18n ---
        self.assertEqual(str(response.data['email'][0]), 'Este campo es requerido.')

    def test_register_with_multiple_missing_fields_fails(self):
        # ...
        # Arrange
        incomplete_payload = {
            'email': 'test@example.com',
            'first_name': 'Test'
        }

        # Act
        response = self.client.post(self.register_url, incomplete_payload, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tenant_name', response.data)
        self.assertIn('password', response.data)
        self.assertIn('last_name', response.data)
        # --- CORRECCIÓN i18n ---
        self.assertEqual(str(response.data['password'][0]), 'Este campo es requerido.')