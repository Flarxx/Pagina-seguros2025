from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import ProductoPoliza, Poliza
from .forms import AdquirirPolizaForm


@login_required
def catalogo_polizas(request):
    form = AdquirirPolizaForm()  # crea el formulario con el queryset de productos
    return render(request, 'polizas/catalogo.html', {'form': form})


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
