# products/serializers.py
from rest_framework import serializers
from .models import Product, RecipeIngredient
from inventory.models import RawMaterial
from tenants.models import Tenant


class RecipeIngredientSerializer(serializers.ModelSerializer):
    # Para ESCRITURA: El frontend enviará el ID de la materia prima.
    # Cambiamos el source para que 'validated_data' contenga 'raw_material'
    raw_material = serializers.PrimaryKeyRelatedField(
        queryset=RawMaterial.objects.all(),
        write_only=True
    )
    # Para LECTURA: El frontend recibirá detalles útiles de la materia prima.
    id = serializers.IntegerField(source='raw_material.id', read_only=True)
    name = serializers.CharField(source='raw_material.name', read_only=True)
    unit_of_measure = serializers.CharField(source='raw_material.unit_of_measure', read_only=True)

    class Meta:
        model = RecipeIngredient
        # 'raw_material' se usa para escribir, los otros para leer.
        fields = ['id', 'raw_material', 'name', 'unit_of_measure', 'quantity']


class ProductSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(
        queryset=Tenant.objects.all(),
        write_only=True,
        required=False
    )
    recipe_ingredients = RecipeIngredientSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id', 'tenant', 'name', 'category', 'description', 'sale_price', 'stock',
            'created_at', 'updated_at',
            'recipe_ingredients'
        ]
        read_only_fields = ['stock']

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Product.objects.all(),
                fields=['tenant', 'name'],
                message="Ya existe un producto con este nombre en tu empresa."
            )
        ]

    def validate_sale_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El precio de venta no puede ser negativo.")
        return value

    def validate_recipe_ingredients(self, ingredients_data):
        tenant = self.context['request'].user.tenant
        if not tenant:
            raise serializers.ValidationError("El usuario no tiene una empresa asociada.")
        for ingredient in ingredients_data:
            raw_material = ingredient['raw_material']
            if raw_material.tenant != tenant:
                raise serializers.ValidationError(
                    f"La materia prima '{raw_material.name}' no pertenece a tu empresa."
                )
        return ingredients_data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', [])
        product = Product.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(product=product, **ingredient_data)
        return product

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', None)

        instance = super().update(instance, validated_data)

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            for ingredient_data in ingredients_data:
                # La clave en 'ingredient_data' es 'raw_material' gracias al PrimaryKeyRelatedField.
                # El modelo espera 'raw_material' (la instancia) o 'raw_material_id' (el ID).
                # Como 'ingredient_data' contiene la instancia del modelo, esto funciona.
                RecipeIngredient.objects.create(product=instance, **ingredient_data)

        return instance