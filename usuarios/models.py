from django.db import models
from django.contrib.auth.models import User
import os
import uuid

def renombrar_documento(instance, filename):
    """Renombra el archivo subido para seguridad y unicidad"""
    ext = filename.split('.')[-1]
    # Genera un nombre único usando UUID
    nuevo_nombre = f'documento_{instance.usuario.id}_{uuid.uuid4().hex}.{ext}'
    return os.path.join('documentos/', nuevo_nombre)

class Perfil(models.Model):
    ROLES = (
        ('admin', 'Administrador'),
        ('agent', 'Agente'),
        ('client', 'Cliente'),
        ('finance', 'Finanzas'),
    )

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    documento_id = models.FileField(
        upload_to=renombrar_documento,
        blank=True,
        null=True
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='client')

    def __str__(self):
        return f"{self.usuario.username} ({self.get_rol_display()})"

    # -------------------------------------
    #           PROPIEDADES EXTRA
    # -------------------------------------

    @property
    def polizas_activas(self):
        """Cantidad de pólizas activas del usuario"""
        return self.usuario.polizas.filter(estado='ACTIVA').count()

    @property
    def cotizaciones(self):
        """Todas las cotizaciones del usuario"""
        return self.usuario.cotizaciones.all()

    @property
    def pagos_pendientes(self):
        """Suma de todos los pagos pendientes del usuario"""
        total = 0
        for poliza in self.usuario.polizas.all():
            total += poliza.saldo_pendiente()
        return total

    @property
    def polizas_con_documentos_pendientes(self):
        """Cantidad de pólizas sin documentos adjuntos"""
        return self.usuario.polizas.filter(documentos__isnull=True).count()

    @property
    def documento_pendiente(self):
        """Indica si el usuario no ha subido su documento de identidad"""
        return self.documento_id is None

    @property
    def reclamos_abiertos(self):
        """Cantidad de reclamos abiertos del usuario"""
        if hasattr(self.usuario, 'claims'):
            return self.usuario.claims.filter(estado='ABIERTO').count()
        return 0
