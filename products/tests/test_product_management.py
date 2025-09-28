# Fichero: products/tests/test_product_management.py
# Test Suite para la Historia de Usuario HU-04: Gestión de Productos Terminados

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import User
from tenants.models import Tenant
from products.models import Product
from decimal import Decimal


class ProductManagementSecurityTests(APITestCase):
    """
    Valida el CRUD completo para Productos Terminados, con un enfoque crítico
    en el aislamiento de datos multi-tenant, validaciones de negocio y la
    correcta inicialización de campos.
    """

    def setUp(self):
        """
        Arrange: Prepara un entorno con dos tenants distintos (A y B) y
        un usuario para cada uno, similar a las pruebas de inventario.
        """
        # --- Tenant A y Usuario A ---
        self.tenant_a = Tenant.objects.create(name="Finca Las Nubes")
        self.user_a = User.objects.create_user(
            email='user_a@nubes.com', password='password123', tenant=self.tenant_a,
            first_name='Usuario', last_name='A'
        )

        # --- Tenant B y Usuario B ---
        self.tenant_b = Tenant.objects.create(name="Cafetal El Sol")
        self.user_b = User.objects.create_user(
            email='user_b@elsol.com', password='password123', tenant=self.tenant_b,
            first_name='Usuario', last_name='B'
        )

        # Autenticamos al cliente por defecto como Usuario A
        self.client.force_authenticate(user=self.user_a)

        # Datos base para un producto válido
        self.valid_product_data = {
            'name': 'Café Tostado Premium',
            'category': 'Tostado Medio',
            'description': 'Un café balanceado con notas a chocolate.',
            'sale_price': '25.50'
        }

    def test_crud_flow_for_own_product(self):
        """
        Verifica el flujo CRUD completo (POST, GET, PUT, PATCH, DELETE).
        Corresponde a TEST-24.
        """
        # 1. CREATE
        url = reverse('product-list')  # Asume basename='product'
        response = self.client.post(url, self.valid_product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.filter(tenant=self.tenant_a).count(), 1)
        self.assertEqual(Decimal(response.data['stock']), Decimal('0.00'))  # Verifica inicialización de stock
        product_id = response.data['id']

        # 2. LIST / RETRIEVE
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        detail_url = reverse('product-detail', kwargs={'pk': product_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. UPDATE (PUT)
        put_data = self.valid_product_data.copy()
        put_data['name'] = 'Café Tostado Gold Edition'
        put_data['sale_price'] = '29.99'
        response = self.client.put(detail_url, put_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Café Tostado Gold Edition')

        # 4. UPDATE (PATCH)
        patch_data = {'description': 'Una selección exclusiva de nuestros mejores granos.'}
        response = self.client.patch(detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], patch_data['description'])

        # 5. DELETE
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.filter(tenant=self.tenant_a).count(), 0)

    def test_user_cannot_list_products_from_other_tenant(self):
        """
        Verifica que la lista de productos está aislada por tenant.
        Corresponde a TEST-25.
        """
        # Arrange: Tenant B crea un producto
        Product.objects.create(tenant=self.tenant_b, name="Té Verde Especial")

        # Act: Usuario A (autenticado por defecto) lista los productos
        url = reverse('product-list')
        response = self.client.get(url)

        # Assert: La lista del Usuario A debe estar vacía
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_user_cannot_access_product_from_other_tenant_by_id(self):
        """
        Verifica que el acceso directo por ID a un producto de otro tenant
        devuelve 404 Not Found (CRÍTICO). Corresponde a TEST-26.
        """
        # Arrange: Tenant A crea un producto
        product_a = Product.objects.create(tenant=self.tenant_a, name="Miel de Abeja Pura")

        # Act: Usuario B intenta acceder al producto del Usuario A
        self.client.force_authenticate(user=self.user_b)
        url = reverse('product-detail', kwargs={'pk': product_a.pk})

        # Assert
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, status.HTTP_404_NOT_FOUND)

    def test_duplicate_product_name_is_prevented_within_tenant(self):
        """
        Verifica que no se pueden crear productos con el mismo nombre en el mismo tenant.
        Corresponde a TEST-27.
        """
        # Arrange: Creamos un producto inicial
        Product.objects.create(tenant=self.tenant_a, name=self.valid_product_data['name'])

        # Act: Intentamos crear otro con los mismos datos
        url = reverse('product-list')
        response = self.client.post(url, self.valid_product_data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(str(response.data['non_field_errors'][0]),
                         "Ya existe un producto con este nombre en tu empresa.")

    def test_different_tenants_can_have_products_with_same_name(self):
        """
        Verifica que la restricción de nombre único es por tenant.
        Corresponde a TEST-28.
        """
        # Arrange: Usuario A crea un producto
        Product.objects.create(tenant=self.tenant_a, name="Chocolate Artesanal")

        # Act: Usuario B intenta crear un producto con el mismo nombre
        self.client.force_authenticate(user=self.user_b)
        url = reverse('product-list')
        data = {'name': 'Chocolate Artesanal', 'category': 'Dulces'}
        response = self.client.post(url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_cannot_create_product_with_negative_price(self):
        """
        Verifica la validación de precio de venta no negativo.
        Corresponde a TEST-29.
        """
        # Arrange
        url = reverse('product-list')
        data = self.valid_product_data.copy()
        data['sale_price'] = '-10.00'

        # Act
        response = self.client.post(url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('sale_price', response.data)
        self.assertEqual(str(response.data['sale_price'][0]), "El precio de venta no puede ser negativo.")

    def test_stock_field_is_read_only(self):
        """
        Verifica que el campo 'stock' es ignorado en POST y PUT/PATCH.
        Corresponde a TEST-30.
        """
        # Arrange: Crear un producto
        url = reverse('product-list')
        data_with_stock = self.valid_product_data.copy()
        data_with_stock['stock'] = '100.00'  # Intentamos forzar el stock

        # Act (POST)
        response_post = self.client.post(url, data_with_stock, format='json')

        # Assert (POST)
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response_post.data['stock']), Decimal('0.00'),
                         "El stock debe inicializarse en 0, ignorando el valor enviado.")

        # Arrange (PUT)
        product_id = response_post.data['id']
        detail_url = reverse('product-detail', kwargs={'pk': product_id})
        update_data = self.valid_product_data.copy()
        update_data['stock'] = '200.00'

        # Act (PUT)
        response_put = self.client.put(detail_url, update_data, format='json')

        # Assert (PUT)
        self.assertEqual(response_put.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response_put.data['stock']), Decimal('0.00'),
                         "El stock no debe cambiar en una operación PUT.")