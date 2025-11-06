from django.urls import path
from . import views

urlpatterns = [
    path('catalogo/', views.catalogo_polizas, name='catalogo_polizas'),
    path('adquirir/', views.adquirir_poliza, name='adquirir_poliza'),
    path('mis-polizas/', views.mis_polizas, name='mis_polizas'),
]
