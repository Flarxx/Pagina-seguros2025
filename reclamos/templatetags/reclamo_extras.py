from django import template

register = template.Library()

@register.filter
def estado_color(estado):
    colores = {
        'PENDIENTE': 'bg-yellow-600',
        'EN_PROCESO': 'bg-sky-600',
        'APROBADO': 'bg-green-600',
        'RECHAZADO': 'bg-red-600',
    }
    return colores.get(estado, 'bg-gray-600')
