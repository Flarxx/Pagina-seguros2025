from django.db import models
from django.contrib.auth.models import User
from polizas.models import Poliza


class Reclamo(models.Model):
    poliza = models.ForeignKey(Poliza, on_delete=models.CASCADE)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, default='pendiente')  # pendiente, aprobado, rechazado

    def __str__(self):
        return f"Reclamo de {self.cliente.username} - {self.poliza.tipo}"
