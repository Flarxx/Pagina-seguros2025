from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import ProductoPoliza, Poliza , Cotizacion
from .forms import AdquirirPolizaForm
from .utils import calcular_prima
from django.http import JsonResponse
from crm.models import Interaccion

@login_required
def catalogo_polizas(request):
    form = AdquirirPolizaForm()
    cotizaciones = Cotizacion.objects.filter(cliente=request.user).order_by('-fecha')
    return render(request, 'polizas/catalogo.html', {
        'form': form,
        'cotizaciones': cotizaciones
    })

@login_required
def adquirir_poliza(request):
    producto_id = request.GET.get('producto')
    if not producto_id:
        return redirect('catalogo_polizas')

    producto = get_object_or_404(ProductoPoliza, id=producto_id)

    if request.method == 'POST':
        # Crear la póliza
        poliza = Poliza.objects.create(
            poliza_numero=f"P-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            cliente=request.user,
            tipo=producto.tipo,
            prima=producto.prima_base,
            fecha_inicio=timezone.now().date(),
            aseguradora=producto.aseguradora if hasattr(producto, 'aseguradora') else None
        )

        # 🔹 Crear la interacción automática en el CRM
        Interaccion.objects.create(
            cliente=request.user,
            poliza=poliza,
            tipo='EM',  # Email por defecto; puedes cambiar según tu lógica
            nota=f"adquiriste la póliza de {poliza.tipo}",
            estado='RE'  # 'Resuelta' por defecto, ajusta según quieras
        )

        # 🔹 Redirigir automáticamente a registrar_pago
        return redirect('registrar_pago', poliza_id=poliza.id)

    form = AdquirirPolizaForm()
    return render(request, 'polizas/cliente/adquirir_polizas.html', {
        'producto': producto,
        'form': form
    })

@login_required
def mis_polizas(request):
    polizas = request.user.polizas.all()
    return render(request, 'polizas/cliente/mis_polizas.html', {'polizas': polizas})

@login_required
def renovar_poliza(request, poliza_id):
    poliza = get_object_or_404(Poliza, id=poliza_id, cliente=request.user)
    
    # Solo permitir renovación si está próxima a vencer o vencida
    if poliza.fecha_fin and poliza.fecha_fin >= timezone.now().date():
        # Opcional: mostrar mensaje "aún vigente, no se puede renovar"
        return redirect('mis_polizas')

    # Crear nueva póliza (o actualizar fechas de la existente)
    nueva_fecha_inicio = timezone.now().date()
    nueva_fecha_fin = nueva_fecha_inicio.replace(year=nueva_fecha_inicio.year + 1)  # un año de cobertura
    
    # Crear una nueva póliza basada en la anterior
    nueva_poliza = Poliza.objects.create(
        poliza_numero=f"P-{timezone.now().strftime('%Y%m%d%H%M%S')}",
        cliente=request.user,
        tipo=poliza.tipo,
        prima=poliza.prima,
        fecha_inicio=nueva_fecha_inicio,
        fecha_fin=nueva_fecha_fin,
        aseguradora=poliza.aseguradora
    )

    # Registrar interacción en CRM
    Interaccion.objects.create(
        cliente=request.user,
        poliza=nueva_poliza,
        tipo='EM',
        nota=f"Cliente renovó la póliza de {poliza.tipo}",
        estado='RE'
    )

    return redirect('mis_polizas')

@login_required
def cotizaciones_cliente(request):
    cotizaciones = Cotizacion.objects.filter(cliente=request.user)
    return render(request, "polizas/cliente/cotizaciones.html", {
        "cotizaciones": cotizaciones
    })

@login_required
def cotizacion_detalle(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk, cliente=request.user)
    return render(request, "polizas/cliente/cotizacion_detalle.html", {
        "cotizacion": cotizacion
    })


@login_required
def cotizar_producto(request, producto_id):
    producto = get_object_or_404(ProductoPoliza, id=producto_id)
    edad = int(request.GET.get('edad', 30))  # edad por defecto 30
    cobertura_extra = {
        "ambulancia": int(request.GET.get('ambulancia', 0)),
        "hospitalizacion": int(request.GET.get('hospitalizacion', 0))
    }
    
    monto = calcular_prima(producto, edad, cobertura_extra)

    # Guardamos la cotización en la DB
    Cotizacion.objects.create(
        cliente=request.user,
        producto=producto,
        edad=edad,
        cobertura_extra=cobertura_extra,
        monto_estimado=monto
    )

    return JsonResponse({"monto_estimado": monto})




