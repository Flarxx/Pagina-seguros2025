# reclamos/models.py
import uuid
import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError

from polizas.models import Poliza

ESTADOS = [
    ('PENDIENTE', 'Pendiente'),
    ('EN_PROCESO', 'En proceso'),
    ('APROBADO', 'Aprobado'),
    ('RECHAZADO', 'Rechazado'),
    ('CERRADO', 'Cerrado'),
]

PRIORIDADES = [
    ('BAJA','Baja'),
    ('MEDIA','Media'),
    ('ALTA','Alta'),
]


def validar_extension_evidencia(value):
    ext = os.path.splitext(value.name)[1].lower()
    permitidas = ['.jpg', '.jpeg', '.png', '.pdf']
    if ext not in permitidas:
        raise ValidationError("Extensión no permitida. Solo JPG, PNG o PDF.")


def validar_tamano_evidencia(value):
    max_mb = 10
    if value.size > max_mb * 1024 * 1024:
        raise ValidationError(f"El archivo excede el límite de {max_mb} MB.")


def generar_codigo_unico(cliente_id):
    ts = timezone.now().strftime('%Y%m%d%H%M%S')
    suf = uuid.uuid4().hex[:6].upper()
    return f"R-{ts}-{cliente_id}-{suf}"


class Reclamo(models.Model):
    poliza = models.ForeignKey(Poliza, on_delete=models.CASCADE)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)

    motivo = models.CharField(max_length=120, blank=True, null=True)
    descripcion = models.TextField()

    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='MEDIA')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')

    evidencia = models.FileField(
        upload_to='reclamos/evidencias/',
        blank=True, null=True,
        validators=[validar_extension_evidencia, validar_tamano_evidencia]
    )

    asignado_a = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='reclamos_asignados'
    )

    fecha = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    codigo = models.CharField(max_length=60, unique=True, blank=True)

    meta = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = ['-fecha']

    def save(self, *args, **kwargs):
        # generar codigo si no existe
        if not self.codigo:
            cliente_id = self.cliente_id or 'X'
            self.codigo = generar_codigo_unico(cliente_id)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.cliente.username} - {self.get_estado_display()}"

    def get_absolute_url(self):
        return reverse('reclamos:detalle', args=[self.pk])


class HistorialEstado(models.Model):
    reclamo = models.ForeignKey(Reclamo, on_delete=models.CASCADE, related_name='historial')
    estado = models.CharField(max_length=20, choices=ESTADOS)
    nota = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.reclamo.codigo} → {self.get_estado_display()} ({self.fecha:%Y-%m-%d %H:%M})"
