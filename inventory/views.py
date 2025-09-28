# inventory/views.py

from rest_framework import viewsets, status, filters, exceptions # Añadimos 'filters' para búsqueda/ordenamiento
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action  # Añadimos 'action' para métodos personalizados

from .models import RawMaterial, PurchaseBatch, Tenant  # Aseguramos que Tenant está importado
from .serializers import RawMaterialSerializer, PurchaseBatchSerializer, serializers


class BaseTenantViewSet(viewsets.ModelViewSet):
    """
    Un ViewSet base que automáticamente filtra los resultados por el tenant del usuario
    y asigna el tenant al crear un nuevo objeto, validando su existencia.
    """
    permission_classes = [IsAuthenticated]  # Todos los endpoints están protegidos por autenticación

    def get_queryset(self):
        """
        Sobrescribe para filtrar el queryset y devolver solo objetos del tenant del usuario actual.
        Si el usuario no tiene un tenant válido, devuelve un queryset vacío.
        """
        if not hasattr(self.request.user, 'tenant') or self.request.user.tenant is None:
            # Si el usuario no tiene tenant, devolvemos un queryset vacío.
            # Esto evita errores y oculta datos si no hay un tenant válido.
            return self.queryset.none()
        return self.queryset.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        # --- ¡CORRECCIÓN CRÍTICA AQUÍ! ---
        # NO DEBE DEVOLVER UNA Response DIRECTAMENTE. DEBE LANZAR UNA EXCEPCIÓN.
        if not hasattr(self.request.user, 'tenant') or self.request.user.tenant is None:
            raise serializers.ValidationError( # <--- CAMBIO CLAVE
                {"detail": "El usuario no está asociado a una empresa válida. No se puede crear el recurso."},
                code='permission_denied' # Código para el error
            )
        # --- FIN CORRECCIÓN ---
        serializer.save(tenant=self.request.user.tenant)


class RawMaterialViewSet(BaseTenantViewSet):
    queryset = RawMaterial.objects.all().order_by('name')
    serializer_class = RawMaterialSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'total_stock']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        unit_of_measure = self.request.query_params.get('unit_of_measure')
        if unit_of_measure:
            queryset = queryset.filter(unit_of_measure=unit_of_measure)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        if hasattr(request.user, 'tenant') and request.user.tenant is not None:
            data['tenant'] = request.user.tenant.id
        else:
            return Response(
                {"detail": "El usuario no está asociado a una empresa válida para crear una Materia Prima."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        if hasattr(request.user, 'tenant') and request.user.tenant is not None:
            data['tenant'] = request.user.tenant.id
        else:
            return Response(
                {"detail": "El usuario no está asociado a una empresa válida para actualizar una Materia Prima."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    # --- ¡MÉTODO '@action units' AÑADIDO AQUÍ! ---
    @action(detail=False, methods=['get'])
    def units(self, request):
        print("DEBUG: [RawMaterialViewSet.units] Entrando al método units.")
        # No se necesita logger.info aquí a menos que quieras doble log.
        # logger.info("DEBUG: [RawMaterialViewSet.units] Entrando al método units.")

        qs = self.get_queryset()
        units = qs.order_by('unit_of_measure').values_list('unit_of_measure', flat=True).distinct()
        return Response(list(units))
    # --- FIN DEL MÉTODO '@action units' AÑADIDO ---


class PurchaseBatchViewSet(BaseTenantViewSet):
    """
    ViewSet para Lotes de Compra, con paginación, ordenamiento y filtrado por tenant
    y por materia prima.
    """
    queryset = PurchaseBatch.objects.all()
    serializer_class = PurchaseBatchSerializer

    # Habilitamos el ordenamiento
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['purchase_date', 'quantity', 'total_cost']  # Campos por los que se puede ordenar
    ordering = ['-purchase_date']  # Ordenamiento por defecto: más recientes primero

    def get_queryset(self):
        """
        Extiende el filtro de BaseTenantViewSet para añadir filtrado por ID de materia prima.
        """
        queryset = super().get_queryset()  # Aplica el filtro por tenant
        material_id = self.request.query_params.get('material_id')
        if material_id:
            queryset = queryset.filter(raw_material_id=material_id)
        return queryset