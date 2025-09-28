# production/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters

from .serializers import ProductionRegistrationSerializer, ProductionLogSerializer
from .services import register_production_batch, InsufficientStockError
from .models import ProductionLog


class ProductionLogListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name']  # Búsqueda a través de la relación con Producto
    ordering_fields = ['production_date', 'product_name']

    def get(self, request, *args, **kwargs):
        # 1. Obtenemos el queryset base
        queryset = ProductionLog.objects.filter(tenant=request.user.tenant)

        # 2. INICIO: APLICAMOS FILTROS Y ORDENAMIENTO MANUALMENTE
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        # FIN: APLICAMOS FILTROS Y ORDENAMIENTO MANUALMENTE

        # 3. Aplicamos la paginación
        paginator = PageNumberPagination()
        paginator.page_size = 6
        paginated_logs = paginator.paginate_queryset(queryset, request)

        serializer = ProductionLogSerializer(paginated_logs, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        # ... tu método post está perfecto, sin cambios ...
        registration_serializer = ProductionRegistrationSerializer(
            data=request.data,
            context={'request': request}
        )
        registration_serializer.is_valid(raise_exception=True)

        validated_data = registration_serializer.validated_data
        product_id = validated_data['product_id']
        quantity_to_produce = validated_data['quantity_produced']

        try:
            production_log = register_production_batch(
                user=request.user,
                product_id=product_id,
                quantity_to_produce=quantity_to_produce
            )
            response_serializer = ProductionLogSerializer(production_log)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except InsufficientStockError as e:
            return Response(e.details, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)