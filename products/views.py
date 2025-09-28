# products/views.py

from rest_framework import viewsets, status, filters, exceptions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
# --- NUEVAS IMPORTACIONES PARA LA HU-7.1 ---
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from decimal import Decimal
# --- FIN DE NUEVAS IMPORTACIONES ---

# --- LIMPIEZA DE IMPORTACIÓN ---
# La importación doble 'serializers' se ha consolidado en una sola línea.
from .serializers import ProductSerializer, serializers
# --- FIN DE LIMPIEZA ---

from .models import Product
from inventory.views import BaseTenantViewSet


class ProductViewSet(BaseTenantViewSet):
    """
    ViewSet para Productos Terminados, aplicando la lógica de seguridad por tenant y borrado protegido.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['name', 'sale_price', 'stock', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)
        return queryset

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Devuelve una lista de nombres de categorías únicas."""
        qs = self.get_queryset()
        categories = qs.order_by('category').values_list('category', flat=True).distinct()
        return Response(categories)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if hasattr(request.user, 'tenant') and request.user.tenant is not None:
            data['tenant'] = request.user.tenant.id
        else:
            raise serializers.ValidationError(
                {"detail": "El usuario no está asociado a una empresa válida para crear un Producto."},
                code='permission_denied'
            )
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_2_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        if hasattr(request.user, 'tenant') and request.user.tenant is not None:
            data['tenant'] = request.user.tenant.id
        else:
            raise serializers.ValidationError(
                {"detail": "El usuario no está asociado a una empresa válida para actualizar un Producto."},
                code='permission_denied'
            )
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    # --- NUEVA ACCIÓN PARA HU-7.1: GRÁFICO DE EVOLUCIÓN DE STOCK ---
    @action(detail=True, methods=['get'])
    def stock_evolution(self, request, pk=None):
        """
        Calcula la evolución del stock acumulado de un producto a lo largo del tiempo.

        Agrupa los registros de producción por mes y devuelve una serie de datos
        lista para ser consumida por una librería de gráficos.
        """
        # PRINCIPIO: Reutilizamos get_object() para obtener el producto.
        # Esto asegura que se aplique el filtro de tenant, previniendo
        # que un usuario pueda ver datos de un producto que no le pertenece.
        product = self.get_object()

        # Realizamos una única y eficiente consulta a la base de datos.
        monthly_production = product.production_logs.annotate(
            # Truncamos la fecha al primer día del mes para poder agrupar.
            month=TruncMonth('production_date')
        ).values(
            # Agrupamos por el mes truncado.
            'month'
        ).annotate(
            # Sumamos la cantidad producida para cada grupo (mes).
            total_produced=Sum('quantity_produced')
        ).order_by(
            # Ordenamos cronológicamente.
            'month'
        )

        # Procesamos los resultados para construir la respuesta
        labels = []
        data = []
        cumulative_stock = Decimal('0.0')

        for item in monthly_production:
            cumulative_stock += item['total_produced']
            # Formateamos la etiqueta del mes (ej. "Sep 2025")
            labels.append(item['month'].strftime('%b %Y'))
            data.append(cumulative_stock)

        response_data = {
            "labels": labels,
            "data": data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    # --- FIN DE NUEVA ACCIÓN ---