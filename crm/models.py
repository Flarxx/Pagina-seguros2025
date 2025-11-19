from django.db import models
from django.conf import settings
from polizas.models import Poliza

# Tipos de interacción posibles
TIPO_INTERACCION = [
    ('LL', 'Llamada'),
    ('EM', 'Email'),
    ('CH', 'Chat'),
]

# Estados posibles de la interacción
ESTADO_INTERACCION = [
    ('PE', 'Pendiente'),
    ('RE', 'Resuelta'),
    ('CA', 'Cancelada'),
]

class Interaccion(models.Model):
    # Cliente asociado a la interacción
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interacciones_cliente'
    )

    # Agente responsable de la interacción (puede estar vacío)
    agente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interacciones_agente'
    )

    # Poliza relacionada (opcional)
    poliza = models.ForeignKey(
        Poliza,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Tipo de interacción
    tipo = models.CharField(
        max_length=2,
        choices=TIPO_INTERACCION,
        default='EM'
    )

    # Notas de la interacción
    nota = models.TextField()

    # Estado de la interacción
    estado = models.CharField(
        max_length=2,
        choices=ESTADO_INTERACCION,
        default='PE'
    )

    # Fechas automáticas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']  # Las más recientes primero
        verbose_name = 'Interacción'
        verbose_name_plural = 'Interacciones'

    def __str__(self):
        return f"{self.get_tipo_display()} con {self.cliente.username} - {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}"
