from django.contrib import admin
from .models import ProductoPoliza, Poliza

# Registrar ProductoPoliza para poder gestionarlo desde el admin
@admin.register(ProductoPoliza)
class ProductoPolizaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'prima_base', 'disponible')
    list_filter = ('tipo', 'disponible')
    search_fields = ('nombre',)

# También puedes registrar Poliza para ver las pólizas adquiridas
@admin.register(Poliza)
class PolizaAdmin(admin.ModelAdmin):
    list_display = ('poliza_numero', 'cliente', 'tipo', 'aseguradora', 'prima', 'estado', 'fecha_inicio', 'fecha_fin')
    list_filter = ('tipo', 'estado', 'aseguradora')
    search_fields = ('poliza_numero', 'cliente__username', 'aseguradora__nombre')
