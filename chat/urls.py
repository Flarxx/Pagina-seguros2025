from django.urls import path
from . import views

urlpatterns = [
    path('enviar/', views.send_message, name='enviar_mensaje_chat'),
    path('historial/', views.load_history, name='cargar_historial_chat'),
]