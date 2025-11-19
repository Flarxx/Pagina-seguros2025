# polizas/api_urls.py
from rest_framework import routers
from django.urls import path, include
from .api_views import ProductoPolizaViewSet, PolizaViewSet

# Creamos el router
router = routers.DefaultRouter()
router.register(r'productos', ProductoPolizaViewSet, basename='productos')
router.register(r'polizas', PolizaViewSet, basename='polizas')

# URLs de la API
urlpatterns = [
    path('api/', include(router.urls)),
]
