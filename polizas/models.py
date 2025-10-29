from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

class Poliza(models.Model):
    TIPOS_POLIZA = [
        ('SALUD', 'Salud'),
        ('AUTO', 'Automóvil'),
        ('HCM_INDIVIDUAL','H.C.M Individual'),
        ('ACCIDENTES_PERSONALES','Accidentes Personales'),
        ('VIDA_INDIVIDUAL','Vida Individual'),
        ('HOGAR','Hogar'),
        ('FUNERARIO','Servicio Funerario'),
        ('RESP_PATRONAL','Responsabilidad Civil Patronal'),
        ('RESP_EMPRESARIAL','Responsabilidad Civil Empresarial'),
        ('CANCER','Patología de Cáncer'),
        ('CASCO_NAVES','Casco Naves (Lanchas)'),
        ('RESP_EMBARCACION','Responsabilidad Civil Embarcación'),
        ('FIDELIDAD','Fidelidad 3D'),
        ('RESP_GENERAL','Responsabilidad Civil General'),
        ('INCENDIO','Incendio'),
        ('RESP_VEHICULOS','Responsabilidad Civil Vehículos'),
        ('COMBINADO_RESIDENCIA','Combinado de Residencia'),
        ('COBERTURA_AMPLIA','Cobertura Amplia'),
        ('OCUPANTES_VEHICULOS','Ocupantes de Vehículos'),
        ('TODO_RIESGO_INDUSTRIAL','Todo Riesgo Industrial'),
        ('RESP_PROFESIONAL','Responsabilidad Civil Profesional'),
        # añade más si hace falta
    ]

    ESTADO = [
        ('ACTIVA','Activa'),
        ('VENCIDA','Vencida'),
        ('CANCELADA','Cancelada'),
    ]

    poliza_numero = models.CharField(max_length=50, unique=True, default='P-DEFAULT')
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polizas')
    tipo = models.CharField(max_length=50, choices=TIPOS_POLIZA)
    sum_insured = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    prima = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default='ACTIVA')
    documentos = models.FileField(upload_to='polizas/documentos/', blank=True, null=True)
    agente = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='polizas_asignadas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta = models.JSONField(default=dict, blank=True)  # para coberturas extras u otros datos

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.poliza_numero} - {self.get_tipo_display()} ({self.cliente.username})"

    def is_active(self):
        return self.estado == 'ACTIVA'

    def dias_restantes(self):
        if self.fecha_fin:
            return (self.fecha_fin - timezone.now().date()).days
        return None

    def saldo_pendiente(self):
        return self.pagos.filter(pagado=False).aggregate(total=models.Sum('monto'))['total'] or 0
    
class ProductoPoliza(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=50, choices=Poliza.TIPOS_POLIZA)
    cobertura = models.JSONField(default=dict, blank=True)
    prima_base = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Cotizacion(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cotizaciones')
    producto = models.ForeignKey(ProductoPoliza, on_delete=models.CASCADE)
    edad = models.PositiveIntegerField(null=True, blank=True)
    cobertura_extra = models.JSONField(default=dict, blank=True)
    monto_estimado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cotización de {self.cliente.username} - {self.producto.nombre}"

