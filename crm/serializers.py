from rest_framework import serializers
from .models import Interaccion
from django.contrib.auth import get_user_model

User = get_user_model()

class InteraccionSerializer(serializers.ModelSerializer):
    cliente_username = serializers.CharField(source='cliente.username', read_only=True)
    agente_username = serializers.CharField(source='agente.username', read_only=True)

    class Meta:
        model = Interaccion
        fields = [
            'id', 'cliente', 'cliente_username', 'agente', 'agente_username',
            'poliza', 'tipo', 'nota', 'estado',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']
