from django.urls import path
from . import views

app_name = 'usuarios'  # Esto activa el namespace "usuarios"

urlpatterns = [
    # Inicio general
    path('', views.inicio, name='inicio'),  # URL: '/' → usuarios:inicio

    # Inicio específico
    path('cliente/', views.inicio_cliente, name='inicio_cliente'),  # usuarios:inicio_cliente
    path('administrador/', views.inicio_admin, name='inicio_administrador'),  # usuarios:inicio_administrador

    # Autenticación
    path('login/', views.login_view, name='login'),     # usuarios:login
    path('logout/', views.logout_view, name='logout'),  # usuarios:logout
    path('registro/', views.registro, name='registro'), # usuarios:registro

    # Perfil
    path('perfil/', views.perfil, name='perfil'),  # usuarios:perfil
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),  # usuarios:editar_perfil
    path('perfil/documento/<int:perfil_id>/', views.descargar_documento, name='descargar_documento'),  # usuarios:descargar_documento

    # Control de clientes (solo admin)
    path('panel/clientes/', views.control_clientes, name='control_clientes'),  # usuarios:control_clientes
    path('panel/clientes/<int:cliente_id>/', views.detalle_cliente_admin, name='detalle_cliente_admin'),  # usuarios:detalle_cliente_admin
]
