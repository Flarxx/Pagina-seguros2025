from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class CategoriaFAQ(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre

class FAQ(models.Model):
    categoria = models.ForeignKey(CategoriaFAQ, on_delete=models.SET_NULL, null=True, blank=True)
    pregunta = models.CharField(max_length=255)
    respuesta = models.TextField()
    orden = models.PositiveIntegerField(default=0)
    publicado = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('orden', 'pregunta')

    def __str__(self):
        return self.pregunta

class Ticket(models.Model):
    ESTADO_CHOICES = [
        ('ABI', 'Abierto'),
        ('PRO', 'En proceso'),
        ('CER', 'Cerrado'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    asunto = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(max_length=3, choices=ESTADO_CHOICES, default='ABI')
    prioridad = models.CharField(max_length=10, choices=[('BAJA','Baja'),('MEDIA','Media'),('ALTA','Alta')], default='MEDIA')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asunto} ({self.usuario})"

class MensajeTicket(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='mensajes')
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    mensaje = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)
    publico = models.BooleanField(default=False)  # si se quiere mostrar la respuesta al usuario

    def __str__(self):
        return f"Mensaje {self.ticket.id} por {self.autor}"
