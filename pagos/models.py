from django.db import models
from django.utils import timezone
from polizas.models import Poliza

class EmpresaAseguradora(models.Model):
    nombre = models.CharField(max_length=100)
    numero_cuenta = models.CharField(max_length=50, help_text="Número de cuenta bancaria")
    banco = models.CharField(max_length=100)
    tipo_cuenta = models.CharField(max_length=50, blank=True, null=True)
    rif = models.CharField(max_length=20, blank=True, null=True)
    correo_contacto = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.banco}"


class Pago(models.Model):
    poliza = models.ForeignKey('polizas.Poliza', on_delete=models.CASCADE, related_name='pagos')
    aseguradora = models.ForeignKey(EmpresaAseguradora, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(default=timezone.now)
    metodo = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: Transferencia, Pago móvil, etc.")
    referencia = models.CharField(max_length=100, blank=True, null=True, help_text="Número de referencia del pago")
    comprobante = models.ImageField(upload_to='comprobantes/', blank=True, null=True)
    pagado = models.BooleanField(default=False)
    verificado = models.BooleanField(default=False, help_text="Marcar cuando un administrador confirme el pago")
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        estado = "Pagado" if self.pagado else "Pendiente"
        return f"Pago de {self.monto} - {estado} ({self.poliza.poliza_numero})"

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'


