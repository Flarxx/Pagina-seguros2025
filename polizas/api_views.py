# polizas/api_views.py
from rest_framework import viewsets, permissions
from .models import ProductoPoliza, Poliza
from .serializers import ProductoPolizaSerializer, PolizaSerializer

# Permisos personalizados
class EsPropietarioOPersonalAdmin(permissions.BasePermission):
    """
    Permite acceso solo al propietario de la póliza o a administradores.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.cliente == request.user

# ViewSet para Productos
class ProductoPolizaViewSet(viewsets.ModelViewSet):
    queryset = ProductoPoliza.objects.all()
    serializer_class = ProductoPolizaSerializer
    permission_classes = [permissions.IsAuthenticated]  # cualquier usuario logueado puede ver

# ViewSet para Polizas
class PolizaViewSet(viewsets.ModelViewSet):
    queryset = Poliza.objects.all()
    serializer_class = PolizaSerializer
    permission_classes = [permissions.IsAuthenticated, EsPropietarioOPersonalAdmin]

    # Opcional: filtrar solo las pólizas del usuario si no es admin
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Poliza.objects.all()
        return Poliza.objects.filter(cliente=user)
