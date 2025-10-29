from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import ProductoPoliza, Poliza , Cotizacion
from .forms import AdquirirPolizaForm
from django.http import JsonResponse
from .utils import calcular_prima   

@login_required
def catalogo_polizas(request):
    form = AdquirirPolizaForm()  # formulario
    cotizaciones = Cotizacion.objects.filter(cliente=request.user).order_by('-fecha')  # últimas primero

    return render(request, 'polizas/catalogo.html', {
        'form': form,
        'cotizaciones': cotizaciones
    })


@login_required
def adquirir_poliza_form(request):
    if request.method == 'POST':
        form = AdquirirPolizaForm(request.POST)
        if form.is_valid():
            producto = form.cleaned_data['producto']
            Poliza.objects.create(
                poliza_numero=f"P-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                cliente=request.user,
                tipo=producto.tipo,
                prima=producto.prima_base,
                fecha_inicio=timezone.now().date(),
            )
            return redirect('mis_polizas')
    else:
        form = AdquirirPolizaForm()

    return render(request, 'polizas/adquirir_poliza_form.html', {'form': form})


@login_required
def mis_polizas(request):
    polizas = request.user.polizas.all()
    return render(request, 'polizas/mis_polizas.html', {'polizas': polizas})



@login_required
def cotizar_producto(request, producto_id):
    producto = ProductoPoliza.objects.get(id=producto_id)
    edad = int(request.GET.get('edad', 30))
    cobertura_extra = {"ambulancia": 5, "hospitalizacion": 10}  # ejemplo
    monto = calcular_prima(producto, edad, cobertura_extra)

    Cotizacion.objects.create(
        cliente=request.user,
        producto=producto,
        edad=edad,
        cobertura_extra=cobertura_extra,
        monto_estimado=monto
    )

    return JsonResponse({"monto_estimado": monto})

