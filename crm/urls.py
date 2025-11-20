from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.lista_interacciones, name='lista_interacciones'),
    path('crear/', views.crear_interaccion, name='crear_interaccion'),
    path('<int:pk>/editar/', views.editar_interaccion, name='editar_interaccion'),
    path('<int:pk>/detalle/', views.detalle_interaccion, name='detalle_interaccion'),
    path('interacciones-recientes/', views.interacciones_recientes_cliente, name='interacciones_recientes_cliente'),
]
