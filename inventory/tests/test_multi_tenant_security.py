# Fichero: inventory/tests/test_multi_tenant_security.py
# (VERSIÓN FINAL Y PRECISA BASADA EN LOS LOGS DE URL)

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import User
from tenants.models import Tenant
from inventory.models import RawMaterial, PurchaseBatch
from decimal import Decimal


class InventoryMultiTenantSecurityTests(APITestCase):

    def setUp(self):
        # ... (código de setUp sin cambios)
        self.tenant_a = Tenant.objects.create(name="Finca Las Nubes")
        self.user_a = User.objects.create_user(
            email='user_a@nubes.com', password='password123', tenant=self.tenant_a,
            first_name='Usuario', last_name='A'
        )
        self.tenant_b = Tenant.objects.create(name="Cafetal El Sol")
        self.user_b = User.objects.create_user(
            email='user_b@elsol.com', password='password123', tenant=self.tenant_b,
            first_name='Usuario', last_name='B'
        )
        self.client.force_authenticate(user=self.user_a)

    def test_crud_flow_for_own_raw_material(self):
        # 1. CREATE
        url = reverse('raw-material-list')  # <-- CORREGIDO con guion, sin namespace
        data = {'name': 'Café Caturra', 'unit_of_measure': 'kg'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        material_id = response.data['id']

        # 2. LIST / RETRIEVE
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        detail_url = reverse('raw-material-detail', kwargs={'pk': material_id})  # <-- CORREGIDO
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. UPDATE
        update_data = {'name': 'Café Caturra (Modificado)', 'unit_of_measure': 'quintal'}
        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4. DELETE
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cannot_list_materials_from_other_tenant(self):
        RawMaterial.objects.create(tenant=self.tenant_b, name="Fertilizante X", unit_of_measure='bolsa')
        url = reverse('raw-material-list')  # <-- CORREGIDO
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_user_cannot_access_material_from_other_tenant_by_id(self):
        material_a = RawMaterial.objects.create(tenant=self.tenant_a, name="Café Orgánico", unit_of_measure='kg')
        self.client.force_authenticate(user=self.user_b)
        url = reverse('raw-material-detail', kwargs={'pk': material_a.pk})  # <-- CORREGIDO
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, status.HTTP_404_NOT_FOUND)
        response_put = self.client.put(url, {'name': 'Intento de hackeo', 'unit_of_measure': 'hack'}, format='json')
        self.assertEqual(response_put.status_code, status.HTTP_404_NOT_FOUND)
        response_delete = self.client.delete(url)
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_duplicate_material_name_is_prevented_within_tenant(self):
        url = reverse('raw-material-list')  # <-- CORREGIDO
        data = {'name': 'Pesticida Y', 'unit_of_measure': 'litro'}
        RawMaterial.objects.create(tenant=self.tenant_a, name=data['name'], unit_of_measure=data['unit_of_measure'])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_different_tenants_can_have_materials_with_same_name(self):
        material_name = "Semillas de Café"
        RawMaterial.objects.create(tenant=self.tenant_a, name=material_name, unit_of_measure='kg')
        self.client.force_authenticate(user=self.user_b)
        url = reverse('raw-material-list')  # <-- CORREGIDO
        data = {'name': material_name, 'unit_of_measure': 'bolsa'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_batch_for_other_tenant_material(self):
        material_b = RawMaterial.objects.create(tenant=self.tenant_b, name="Abono Especial", unit_of_measure='saco')
        url = reverse('purchase-batch-list')  # <-- CORREGIDO
        data = {
            'raw_material': material_b.pk,
            'purchase_date': '2025-09-04',
            'quantity': 100,
            'total_cost': 5000
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_batch_list_can_be_filtered_by_material(self):
        material_1 = RawMaterial.objects.create(tenant=self.tenant_a, name="Material 1", unit_of_measure='u')
        material_2 = RawMaterial.objects.create(tenant=self.tenant_a, name="Material 2", unit_of_measure='u')
        PurchaseBatch.objects.create(tenant=self.tenant_a, raw_material=material_1, purchase_date='2025-01-01',
                                     quantity=10, total_cost=100)
        PurchaseBatch.objects.create(tenant=self.tenant_a, raw_material=material_1, purchase_date='2025-02-01',
                                     quantity=15, total_cost=150)
        PurchaseBatch.objects.create(tenant=self.tenant_a, raw_material=material_2, purchase_date='2025-03-01',
                                     quantity=20, total_cost=200)
        url = reverse('purchase-batch-list')  # <-- CORREGIDO
        response = self.client.get(url, {'material_id': material_1.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

# Fichero: inventory/tests/test_multi_tenant_security.py
# (AÑADIR ESTE NUEVO MÉTODO AL FINAL DE LA CLASE InventoryMultiTenantSecurityTests)

    def test_quantity_remaining_initializes_correctly_on_batch_create(self):
        """
        Verifica que el nuevo campo 'quantity_remaining' en PurchaseBatch
        se inicializa correctamente con el valor de 'quantity' al crear un lote.
        Corresponde a TEST-31.
        """
        # Arrange
        material = RawMaterial.objects.create(tenant=self.tenant_a, name="Harina de Trigo", unit_of_measure='kg')
        url = reverse('purchase-batch-list')
        batch_data = {
            'raw_material': material.pk,
            'purchase_date': '2025-09-05',
            'quantity': '150.75',
            'total_cost': '300.00'
        }

        # Act
        response = self.client.post(url, batch_data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # El serializador no expone 'quantity_remaining', debemos verificar el objeto en la BD.
        # Esto es una prueba de backend más pura y robusta.
        created_batch = PurchaseBatch.objects.get(pk=response.data['id'])
        self.assertEqual(created_batch.quantity_remaining, created_batch.quantity)
        self.assertEqual(created_batch.quantity_remaining, Decimal('150.75'))