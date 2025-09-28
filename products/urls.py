# products/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

# PRINCIPIO DE LA EXPLICACIÓN ARQUITECTÓNICA
# Se ha identificado que la URL para el ProductViewSet se estaba registrando incorrectamente como '/api/v1/products/products/'.
# Esto se debía a que el `path()` en `centavo/urls.py` ya proveía el prefijo '/api/v1/products/',
# y el `router.register()` aquí añadía un segundo prefijo 'products'.
#
# La corrección consiste en usar un prefijo vacío (r'') en el registro del router.
# De esta manera, las acciones del ViewSet (list, create, retrieve, etc.) se mapean directamente
# a la ruta base proporcionada por el include principal, resultando en la URL correcta: '/api/v1/products/'.
# Esto alinea el comportamiento del ProductViewSet con el de los otros ViewSets del proyecto.
# FIN DE LA EXPLICACIÓN ARQUITECTÓNICA

router = DefaultRouter()
# ANTES (Incorrecto): router.register(r'products', ProductViewSet, basename='products')
router.register(r'', ProductViewSet, basename='products') # DESPUÉS (Correcto): Usamos un prefijo vacío.

urlpatterns = [
    path('', include(router.urls)),
]