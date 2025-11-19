from rest_framework import viewsets, permissions
from .models import Interaccion
from .serializers import InteraccionSerializer

# Permisos personalizados
class EsClienteOAgente(permissions.BasePermission):
    """
    Permite acceso solo al cliente dueño de la interacción,
    al agente asignado, o a un admin.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.cliente == request.user or obj.agente == request.user

class InteraccionViewSet(viewsets.ModelViewSet):
    queryset = Interaccion.objects.all().order_by('-fecha_creacion')
    serializer_class = InteraccionSerializer
    permission_classes = [permissions.IsAuthenticated, EsClienteOAgente]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Interaccion.objects.all().order_by('-fecha_creacion')
        # Clientes ven solo sus interacciones
        return Interaccion.objects.filter(cliente=user).order_by('-fecha_creacion')
