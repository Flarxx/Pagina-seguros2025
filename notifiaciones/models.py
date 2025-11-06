from django.db import models
from django.contrib.auth.models import User


class Notificacion(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.cliente.username} - {'Leída' if self.leida else 'No leída'}"
