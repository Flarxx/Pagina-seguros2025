from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Pago, EmpresaAseguradora
from polizas.models import Poliza
from .forms import PagoForm


@login_required
def registrar_pago(request, poliza_id):
    poliza = get_object_or_404(Poliza, id=poliza_id, cliente=request.user)

    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.poliza = poliza
            pago.fecha_pago = timezone.now().date()

            # Si la póliza tiene aseguradora, la asignamos automáticamente
            if poliza.aseguradora:
                pago.aseguradora = poliza.aseguradora

            pago.save()
            return redirect('mis_pagos')
    else:
        form = PagoForm()

        # Si la póliza tiene aseguradora, ocultamos el campo en el formulario
        if poliza.aseguradora:
            form.fields.pop('aseguradora')

    return render(request, 'pagos/registrar_pago.html', {
        'form': form,
        'poliza': poliza
    })



@login_required
def mis_pagos(request):
    pagos = Pago.objects.filter(poliza__cliente=request.user).select_related('poliza', 'aseguradora')
    return render(request, 'pagos/mis_pagos.html', {'pagos': pagos})
