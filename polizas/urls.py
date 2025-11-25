from django.urls import path, include
from . import views
from rest_framework import routers
from .api_views import ProductoPolizaViewSet, PolizaViewSet
from .views import cotizaciones_cliente
from .views import cotizacion_detalle   

app_name = 'polizas'
# ----------------------------
# Router para la API
# ----------------------------
router = routers.DefaultRouter()
router.register(r'productos', ProductoPolizaViewSet)
router.register(r'polizas', PolizaViewSet)

# ----------------------------
# URLs normales
# ----------------------------
urlpatterns = [
    path('catalogo/', views.catalogo_polizas, name='catalogo_polizas'),
    path('adquirir/', views.adquirir_poliza, name='adquirir_poliza'),
    path('mis-polizas/', views.mis_polizas, name='mis_polizas'),
    # Incluir las rutas de la API
    path('api/', include(router.urls)),
    path('renovar/<int:poliza_id>/', views.renovar_poliza, name='renovar_poliza'),
    path("cotizaciones/", cotizaciones_cliente, name="cotizaciones_cliente"),
    path("cotizacion/<int:pk>/", cotizacion_detalle, name="cotizacion_detalle")

]
