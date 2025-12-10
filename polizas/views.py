from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import ProductoPoliza, Poliza , Cotizacion
from .forms import AdquirirPolizaForm, PerfilFamiliarForm
from .utils import calcular_prima
from django.http import JsonResponse
from crm.models import Interaccion
import json
from datetime import timedelta


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
        return redirect('pagos:registrar_pago', poliza_id=poliza.id)

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
    
    # 1. INSTANCIAR el formulario de perfil
    form = PerfilFamiliarForm(request.GET) # Usamos GET para que la URL sea compartible
    
    productos_ordenados = None
    titulo_cotizacion = None
    edades_json = None
    deducible_por_defecto = 2500
    
    # 2. PROCESAR DATOS del formulario si existen (el usuario ha cotizado)
    if form.is_valid():
        data = form.cleaned_data
        
        # A. Construir el diccionario de edades real (para calcular_prima)
        edades_del_grupo = {
            'titular': data['edad_titular'],
        }
        
        titulo_parts = [f"Titular {data['edad_titular']} años"]
        
        # Añadir dependiente adulto
        if data['num_dependientes_adultos'] == 1 and data['edad_dependiente_adulto']:
            edades_del_grupo['esposa'] = data['edad_dependiente_adulto']
            titulo_parts.append(f"Pareja {data['edad_dependiente_adulto']} años")

        # Añadir hijos (se simulan múltiples hijos con una sola edad)
        if data['num_hijos'] > 0 and data['edad_promedio_hijos']:
            for i in range(1, data['num_hijos'] + 1):
                edades_del_grupo[f'hijo{i}'] = data['edad_promedio_hijos']
            
            titulo_parts.append(f"{data['num_hijos']} Hijos (Edad Mayor: {data['edad_promedio_hijos']})")
        
        titulo_cotizacion = " + ".join(titulo_parts)
        edades_json = json.dumps(edades_del_grupo)


        # B. Obtener Productos y Calcular Primas (Paso 2 de la lógica anterior)
        productos = ProductoPoliza.objects.filter(tipo='SALUD', disponible=True)
        productos_cotizados = []

        for producto in productos:
            prima_calculada = calcular_prima(
                producto, 
                edades_del_grupo, 
                deducible_por_defecto
            )
            
            setattr(producto, 'prima_mensual_calculada', prima_calculada)
            setattr(producto, 'deducible_actual', deducible_por_defecto)
            productos_cotizados.append(producto)

        productos_ordenados = sorted(productos_cotizados, key=lambda p: p.prima_mensual_calculada)
    
    # --- Lógica del Historial de Cotizaciones (Tu lógica original) ---
    historial_cotizaciones = Cotizacion.objects.filter(cliente=request.user).order_by('-fecha')
    
    
    # --- Contexto Final ---
    context = {
        "form_perfil": form, # <-- Pasamos el formulario a la plantilla
        "cotizaciones_historial": historial_cotizaciones,
        
        'productos': productos_ordenados, # Será None si no hay datos de cotización
        'titulo_cotizacion': titulo_cotizacion,
        'edades_json': edades_json, 
        'deducible_por_defecto': deducible_por_defecto, # Para el slider inicial
    }
    
    return render(request, "polizas/cliente/cotizaciones.html", context)


# --- Endpoint AJAX para ajuste dinámico de Prima (Mantenemos esta vista) ---
@require_POST
@login_required
def ajustar_prima_ajax(request):
    """Recibe un producto ID y un nuevo deducible, calcula la prima y devuelve JSON."""
    
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        nuevo_deducible = int(data.get('deducible', 2500)) 
        edades_grupo = data.get('edades_grupo') # Edades necesarias para el cálculo

        if not producto_id or not edades_grupo:
            return HttpResponseBadRequest(json.dumps({'error': 'Faltan parámetros'}), content_type='application/json')

        producto = ProductoPoliza.objects.get(id=producto_id)

        prima_ajustada = calcular_prima(producto, edades_grupo, nuevo_deducible)

        return JsonResponse({
            'producto_id': producto_id,
            'nueva_prima': prima_ajustada,
            'nuevo_deducible': nuevo_deducible,
        })

    except ProductoPoliza.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)

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

def cotizar_publico(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        telefono = request.POST.get("telefono")
        email = request.POST.get("email")
        tipo = request.POST.get("tipo")
        suma_asegurada = float(request.POST.get("suma_asegurada"))

        # Calcular prima (puedes usar tu propio cálculo)
        prima = suma_asegurada * 0.02

        # Crear la cotización
        cotizacion = Cotizacion.objects.create(
            nombre=nombre,
            telefono=telefono,
            email=email,
            tipo_poliza=tipo,
            suma_asegurada=suma_asegurada,
            prima_estimada=prima,
            fecha_expiracion=timezone.now() + timedelta(days=7),
            meta={"origen": "publico"}
        )
        
        return redirect('cotizacion_generada', id=cotizacion.id)

    return render(request, 'polizas/publico/cotizar_publico.html')



def cotizacion_generada(request, id):
    cotizacion = get_object_or_404(Cotizacion, id=id)
    return render(request, 'polizas/publico/cotizacion_generada.html', {
        "cotizacion": cotizacion
    })




