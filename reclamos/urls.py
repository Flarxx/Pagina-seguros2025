# reclamos/urls.py
from django.urls import path
from . import views

app_name = "reclamos"  # Esto es obligatorio para usar {% url 'reclamos:crear' %}

urlpatterns = [
    path('', views.mis_reclamos_cliente, name='mis_reclamos'),
    path('crear/', views.crear_reclamo, name='crear'),
    path('<int:pk>/', views.detalle_reclamo, name='detalle'),
    path('<int:pk>/editar/', views.editar_reclamo, name='editar'),
    path('<int:pk>/subir-evidencia/', views.subir_evidencia, name='subir_evidencia'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado, name='cambiar_estado'),
    path('recientes/json/', views.reclamos_json_recientes, name='json_recientes'),
]
