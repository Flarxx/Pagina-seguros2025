from django.db import models
from django.contrib.auth.models import User


class Poliza(models.Model):
    TIPOS_POLIZA = [
        ('SALUD', 'Salud'),
        ('AUTO', 'Automóvil'),
    ]

    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS_POLIZA)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_fin = models.DateField(blank=True, null=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tipo} - {self.cliente.username}"
