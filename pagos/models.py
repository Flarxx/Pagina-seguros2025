from django.db import models
from django.utils import timezone  # ✅ IMPORTANTE
from polizas.models import Poliza  # si estás relacionando con Poliza

class Pago(models.Model):
    poliza = models.ForeignKey('polizas.Poliza', on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(default=timezone.now)
    pagado = models.BooleanField(default=False)  # <- esta es la correcta
    metodo = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        estado = "Pagado" if self.pagado else "Pendiente"
        return f"Pago {self.monto} - {estado} ({self.poliza.poliza_numero})"

