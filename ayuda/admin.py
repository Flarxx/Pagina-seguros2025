from django.contrib import admin
from .models import CategoriaFAQ, FAQ, Ticket, MensajeTicket

@admin.register(CategoriaFAQ)
class CategoriaFAQAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('pregunta', 'categoria', 'publicado', 'orden')
    list_filter = ('categoria', 'publicado')
    search_fields = ('pregunta', 'respuesta')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('asunto','usuario','estado','prioridad','creado')
    list_filter = ('estado','prioridad')
    search_fields = ('asunto','descripcion','usuario__username')

@admin.register(MensajeTicket)
class MensajeTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'autor', 'creado')
    search_fields = ('mensaje',)

