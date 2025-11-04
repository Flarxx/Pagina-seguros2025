from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Pago, EmpresaAseguradora
from polizas.models import Poliza
from .forms import PagoForm  # la crearemos enseguida

@login_required
def registrar_pago(request, poliza_id):
    # Solo permite que el cliente acceda a sus propias pólizas
    poliza = get_object_or_404(Poliza, id=poliza_id, cliente=request.user)

    # Si la póliza ya tiene aseguradora asignada, la usamos; sino, mostramos todas
    aseguradoras = [poliza.aseguradora] if poliza.aseguradora else EmpresaAseguradora.objects.all()

    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.poliza = poliza
            pago.fecha_pago = timezone.now().date()
            pago.save()
            return redirect('mis_pagos')  # Redirige a lista de pagos del cliente
    else:
        form = PagoForm()

    return render(request, 'pagos/registrar_pago.html', {
        'form': form,
        'poliza': poliza,
        'aseguradoras': aseguradoras
    })


@login_required
def mis_pagos(request):
    pagos = Pago.objects.filter(poliza__cliente=request.user).select_related('poliza', 'aseguradora')
    return render(request, 'pagos/mis_pagos.html', {'pagos': pagos})
