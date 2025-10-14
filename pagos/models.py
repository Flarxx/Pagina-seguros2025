from django.db import models
from django.contrib.auth.models import User
from polizas.models import Poliza  # IMPORT CORRECTO


class Pago(models.Model):
    poliza = models.ForeignKey(Poliza, on_delete=models.CASCADE)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, default='pendiente')  # pendiente, aprobado, rechazado

    def __str__(self):
        return f"Pago de {self.cliente.username} - {self.monto} ({self.estado})"
