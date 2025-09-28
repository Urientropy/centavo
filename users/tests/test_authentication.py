# Fichero: users/tests/test_authentication.py
# Test Suite para la Historia de Usuario HU-1.2 (VERSIÓN FINAL CALIBRADA)

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import User
from tenants.models import Tenant


class AuthenticationFlowAPITests(APITestCase):
    """
    Pruebas que cubren el flujo completo de autenticación: login,
    refresco de token y logout, especificado en la HU-1.2.
    """

    def setUp(self):
        self.tenant = Tenant.objects.create(name="Finca de Pruebas")
        self.email = 'testlogin@example.com'
        self.password = 'a_very_secure_password_!@#'

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            tenant=self.tenant,
            first_name='Test',
            last_name='User'
        )

        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.logout_url = reverse('auth_logout')

    def test_user_can_login_with_valid_credentials(self):
        # ... (Pasa, no necesita cambios)
        login_data = {'email': self.email, 'password': self.password}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_fails_with_incorrect_password(self):
        # ... (Pasa, no necesita cambios)
        login_data = {'email': self.email, 'password': 'wrong_password'}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_login_fails_with_nonexistent_user(self):
        # ...
        login_data = {'email': 'nosuchuser@example.com', 'password': 'any_password'}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        # --- CORRECCIÓN i18n ---
        self.assertEqual(str(response.data['detail']),
                         'No se encontró una cuenta activa con las credenciales proporcionadas.')

    def test_valid_refresh_token_generates_new_access_token(self):
        # ... (Pasa, no necesita cambios)
        login_data = {'email': self.email, 'password': self.password}
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        refresh_payload = {'refresh': refresh_token}
        response = self.client.post(self.refresh_url, refresh_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_logout_blacklists_refresh_token(self):
        # ... (Pasa, no necesita cambios)
        login_data = {'email': self.email, 'password': self.password}
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']
        logout_payload = {'refresh': refresh_token}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(self.logout_url, logout_payload, format='json')
        self.assertIn(response.status_code,
                      [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT, status.HTTP_205_RESET_CONTENT])
        refresh_payload = {'refresh': refresh_token}
        reuse_response = self.client.post(self.refresh_url, refresh_payload, format='json')
        self.assertEqual(reuse_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(str(reuse_response.data['code']), 'token_not_valid')

    def test_logout_endpoint_is_protected(self):
        # ...
        self.client.credentials()
        logout_payload = {'refresh': 'any_fake_token'}
        response = self.client.post(self.logout_url, logout_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # --- CORRECCIÓN i18n ---
        self.assertEqual(str(response.data['detail']), 'Las credenciales de autenticación no se proveyeron.')