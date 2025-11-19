from rest_framework import serializers
from .models import ProductoPoliza, Poliza

# -------------------------------
# Serializer para ProductoPoliza
# -------------------------------
class ProductoPolizaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoPoliza
        fields = ['id', 'nombre', 'tipo', 'prima_base', 'disponible']  # campos que quieres exponer


# -------------------------------
# Serializer para Poliza
# -------------------------------
class PolizaSerializer(serializers.ModelSerializer):
    # Mostrar el nombre del producto y el cliente como texto
    producto = serializers.StringRelatedField()  # nombre del ProductoPoliza
    cliente = serializers.StringRelatedField()   # username del cliente

    class Meta:
        model = Poliza
        fields = [
            'id',
            'poliza_numero',
            'cliente',
            'producto',
            'tipo',
            'aseguradora',
            'prima',
            'estado',
            'fecha_inicio',
            'fecha_fin',
        ]
        read_only_fields = ['poliza_numero']  # este campo lo generas automáticamente
