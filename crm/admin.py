# crm/admin.py
from django.contrib import admin
from .models import Interaccion

@admin.register(Interaccion)
class InteraccionAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'agente', 'tipo', 'estado', 'poliza', 'fecha_creacion')
    list_filter = ('tipo', 'estado', 'fecha_creacion')
    search_fields = ('cliente__username', 'agente__username', 'nota')
