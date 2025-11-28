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
    ]

    ESTADO = [
        ('ACTIVA', 'Activa'),
        ('PEND_VERIF', 'Pago pendiente de verificación'),
        ('VENCIDA', 'Vencida'),
        ('CANCELADA', 'Cancelada'),
    ]

    poliza_numero = models.CharField(max_length=50, unique=True, default='P-DEFAULT')
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polizas')
    tipo = models.CharField(max_length=50, choices=TIPOS_POLIZA)
    aseguradora = models.ForeignKey(
    'pagos.EmpresaAseguradora',  # referencia por string evita el import circular
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='polizas'
)
    sum_insured = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    prima = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=50, choices=ESTADO, default='ACTIVA')
    documentos = models.FileField(upload_to='polizas/documentos/', blank=True, null=True)
    agente = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='polizas_asignadas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta = models.JSONField(default=dict, blank=True)  # Coberturas extras u otros datos

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
        return self.pagos.filter(estado_pago='pendiente').aggregate(total=models.Sum('monto'))['total'] or 0

    
class ProductoPoliza(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    # Asumo que 'Poliza' está disponible en el scope o importado correctamente
    tipo = models.CharField(max_length=50, choices=Poliza.TIPOS_POLIZA) 
    cobertura = models.JSONField(default=dict, blank=True)
    prima_base = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    # Campos específicos para la Cotización (Tarjeta)
    nombre_aseguradora = models.CharField(max_length=100, default='Aseguradora X')
    deducible_dentro_usa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deducible_fuera_usa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cobertura_maxima = models.DecimalField(max_digits=12, decimal_places=2)

    etiqueta_destacada = models.CharField(
        max_length=50, 
        choices=[
            ('RECOMENDADO', 'Recomendado'), 
            ('COMPLETO', 'Más Completo'), 
            ('ALTERNATIVA', 'La Alternativa'),
            ('MAXIMA', 'Máxima'),
            ('BUENA_OPCION', 'Buena Opción'),
            ('-', 'Sin Etiqueta')
        ],
        default='-',
    )
    
    prima_desde = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prima_hasta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    detalles_extras = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


# polizas/models.py
class Cotizacion(models.Model):
    cliente = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='cotizaciones')
    nombre = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, default='0000000000')
    mail = models.EmailField(default='no_aplica@seguros.com')
    tipo_poliza = models.CharField(max_length=50, choices=Poliza.TIPOS_POLIZA, default='SALUD')
    suma_asegurada = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    prima_estimada = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cotización {self.tipo_poliza} - {self.email}"


