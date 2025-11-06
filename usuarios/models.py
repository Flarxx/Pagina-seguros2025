from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    documento_id = models.FileField(upload_to='documentos/', blank=True, null=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='client')

    def __str__(self):
        return f"{self.usuario.username} ({self.get_rol_display()})"

    # -------------------------
    # Propiedades útiles
    # -------------------------

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
        """Cantidad de pólizas que no tienen documentos adjuntos"""
        return self.usuario.polizas.filter(documentos__isnull=True).count()

    @property
    def documento_pendiente(self):
        """Si el usuario no ha subido su documento de identidad"""
        return self.documento_id is None

    @property
    def reclamos_abiertos(self):
        """Cantidad de reclamos abiertos (requiere modelo Claim)"""
        if hasattr(self.usuario, 'claims'):
            return self.usuario.claims.filter(estado='ABIERTO').count()
        return 0

    
    

