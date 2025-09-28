# inventory/urls.py

from rest_framework.routers import DefaultRouter
from .views import RawMaterialViewSet, PurchaseBatchViewSet

router = DefaultRouter()
router.register(r'raw-materials', RawMaterialViewSet, basename='raw-material')
router.register(r'purchase-batches', PurchaseBatchViewSet, basename='purchase-batch')

urlpatterns = router.urls

# --- AÑADE ESTA LÍNEA DE DEBUG ---
import pprint # Para una salida más legible
print("\nDEBUG: [inventory/urls.py] Contenido de urlpatterns del router:")
pprint.pprint([str(p) for p in urlpatterns]) # Muestra los patrones URL generados
print("-" * 50)
# --- FIN DE DEBUG ---