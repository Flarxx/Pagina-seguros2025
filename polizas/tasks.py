from django.utils import timezone
from .models import Poliza

def actualizar_estado_polizas():
    hoy = timezone.now().date()
    Poliza.objects.filter(fecha_fin__lt=hoy, estado='ACTIVA').update(estado='VENCIDA')
