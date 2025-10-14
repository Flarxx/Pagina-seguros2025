from django.db import models
from django.contrib.auth.models import User
from polizas.models import Poliza


class Interaccion(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    poliza = models.ForeignKey(Poliza, on_delete=models.SET_NULL, null=True, blank=True)
    nota = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interacción con {self.cliente.username} - {self.fecha}"
