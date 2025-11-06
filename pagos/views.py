from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.contrib import messages
from .models import Pago
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
            pago.estado_pago = 'pendiente'  # 👈 Nuevo estado por defecto
            if poliza.aseguradora:
                pago.aseguradora = poliza.aseguradora
            pago.save()

            messages.success(request, "✅ Tu pago fue registrado correctamente y está pendiente de verificación.")
            return redirect('mis_pagos')
    else:
        form = PagoForm()

    if poliza.aseguradora and 'aseguradora' in form.fields:
        form.fields.pop('aseguradora')

    return render(request, 'pagos/cliente/registrar_pago.html', {
        'form': form,
        'poliza': poliza
    })


@login_required
def mis_pagos(request):
    pagos = Pago.objects.filter(poliza__cliente=request.user).select_related('poliza', 'aseguradora')
    return render(request, 'pagos/cliente/mis_pagos.html', {'pagos': pagos})


@staff_member_required
def verificar_pagos(request):
    pagos = Pago.objects.select_related('poliza', 'aseguradora').order_by('-fecha_registro')

    if request.method == 'POST':
        pago_id = request.POST.get('pago_id')
        accion = request.POST.get('accion')
        pago = get_object_or_404(Pago, id=pago_id)

        if accion == 'aprobar':
            pago.estado_pago = 'aprobado'
            pago.poliza.estado = 'ACTIVA'
            pago.poliza.save()
            messages.success(request, f"✅ Pago {pago.id} aprobado correctamente.")
        elif accion == 'rechazar':
            pago.estado_pago = 'rechazado'
            messages.error(request, f"❌ Pago {pago.id} rechazado.")
        
        pago.save()
        return redirect('verificar_pagos')

    return render(request, 'pagos/admin/verificar_pagos.html', {'pagos': pagos})
