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


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    instance.perfil.save()
