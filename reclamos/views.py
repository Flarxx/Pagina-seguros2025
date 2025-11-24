# reclamos/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.contrib import messages
from django.db import transaction

from .models import Reclamo, HistorialEstado
from .forms import (
    ReclamoClienteForm, ReclamoStaffForm,
    EvidenciaForm, CambiarEstadoForm
)

# integración CRM: usa el modelo Interaccion que ya tienes en crm.models
try:
    from crm.models import Interaccion
except Exception:
    Interaccion = None  # si no existe, no romperá; solo no se registrarán interacciones

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import strip_tags


# -------------------------
# Helpers
# -------------------------
def es_agent(user):
    try:
        return hasattr(user, 'perfil') and user.perfil.rol == 'agent'
    except Exception:
        return False


def puede_ver_reclamo(user, reclamo: Reclamo):
    if user.is_staff:
        return True
    if reclamo.cliente == user:
        return True
    if es_agent(user) and (reclamo.asignado_a == user or reclamo.asignado_a is None):
        return True
    return False


def puede_editar_reclamo(user, reclamo: Reclamo):
    estados_editables = ['PENDIENTE', 'EN_PROCESO']
    return reclamo.cliente == user and reclamo.estado in estados_editables


def es_hx_request(request):
    # htmx sets HX-Request: true
    return request.headers.get('HX-Request') == 'true' or request.headers.get('x-requested-with') == 'XMLHttpRequest'


# -------------------------
# Vistas
# -------------------------
@login_required
def mis_reclamos_cliente(request):
    reclamos = Reclamo.objects.filter(cliente=request.user).select_related('poliza', 'asignado_a')
    # Añade flag si es agent para templates
    context = {'reclamos': reclamos, 'is_agent': es_agent(request.user)}
    return render(request, 'reclamos/mis_reclamos.html', context)


@login_required
def crear_reclamo(request):
    if request.method == 'POST':
        form = ReclamoClienteForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                r = form.save(commit=False)
                r.cliente = request.user
                r.save()
                HistorialEstado.objects.create(reclamo=r, estado=r.estado, nota='Reclamo creado', usuario=request.user)
                # registrar en CRM si existe
                if Interaccion:
                    try:
                        Interaccion.objects.create(
                            cliente=request.user,
                            poliza=r.poliza,
                            tipo='EM',
                            nota=f"Reclamo creado: {r.codigo} - {strip_tags(r.descripcion)[:240]}",
                            estado='PE' if hasattr(Interaccion, 'estado') else None
                        )
                    except Exception:
                        pass
                messages.success(request, "Reclamo creado correctamente.")
                return redirect(r.get_absolute_url())
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        initial = {}
        poliza_get = request.GET.get('poliza')
        if poliza_get:
            initial['poliza'] = poliza_get
        form = ReclamoClienteForm(initial=initial)
    return render(request, 'reclamos/cliente/crear_reclamo.html', {'form': form})



@login_required
def detalle_reclamo(request, pk):
    reclamo = get_object_or_404(Reclamo.objects.select_related('poliza', 'asignado_a'), pk=pk)
    if not puede_ver_reclamo(request.user, reclamo):
        return HttpResponseForbidden("No tienes permiso para ver este reclamo.")
    evidencia_form = EvidenciaForm()
    cambiar_estado_form = CambiarEstadoForm()
    context = {
        'reclamo': reclamo,
        'evidencia_form': evidencia_form,
        'cambiar_estado_form': cambiar_estado_form,
        'is_agent': es_agent(request.user),
    }
    return render(request, 'reclamos/cliente/detalle.html', context)


@login_required
def editar_reclamo(request, pk):
    reclamo = get_object_or_404(Reclamo, pk=pk)
    if request.user.is_staff or es_agent(request.user):
        form_class = ReclamoStaffForm
    else:
        if not puede_editar_reclamo(request.user, reclamo):
            messages.error(request, "No puedes editar este reclamo (permiso o estado).")
            return redirect('reclamos:detalle', pk=reclamo.pk)
        form_class = ReclamoClienteForm

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=reclamo)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                HistorialEstado.objects.create(reclamo=reclamo, estado=reclamo.estado, nota='Reclamo editado', usuario=request.user)
                if Interaccion:
                    try:
                        Interaccion.objects.create(
                            cliente=reclamo.cliente,
                            poliza=reclamo.poliza,
                            tipo='EM',
                            nota=f"Reclamo {reclamo.codigo} editado por {request.user.username}",
                            estado='PE' if hasattr(Interaccion, 'estado') else None
                        )
                    except Exception:
                        pass
                messages.success(request, "Reclamo actualizado.")
                return redirect('reclamos:detalle', pk=reclamo.pk)
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = form_class(instance=reclamo)

    return render(request, 'reclamos/editar_reclamo.html', {'form': form, 'reclamo': reclamo})


# -------------------------
# Subir evidencia (htmx-friendly)
# -------------------------
@login_required
@require_POST
def subir_evidencia(request, pk):
    reclamo = get_object_or_404(Reclamo, pk=pk)
    if not puede_ver_reclamo(request.user, reclamo):
        return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)

    form = EvidenciaForm(request.POST, request.FILES, instance=reclamo)
    if form.is_valid():
        with transaction.atomic():
            form.save()
            HistorialEstado.objects.create(reclamo=reclamo, estado=reclamo.estado, nota='Evidencia subida', usuario=request.user)
            if Interaccion:
                try:
                    Interaccion.objects.create(
                        cliente=reclamo.cliente,
                        poliza=reclamo.poliza,
                        tipo='EM',
                        nota=f"Evidencia subida para {reclamo.codigo}",
                        estado='PE' if hasattr(Interaccion, 'estado') else None
                    )
                except Exception:
                    pass

        # Respuesta para htmx: fragmento HTML
        if es_hx_request(request):
            html = '<div class="text-sm text-green-600">Evidencia subida correctamente.</div>'
            return HttpResponse(html)
        # JSON fallback
        return JsonResponse({'ok': True, 'url': reclamo.evidencia.url if reclamo.evidencia else ''})
    else:
        errors = form.errors.as_ul()
        if es_hx_request(request):
            return HttpResponse(f'<div class="text-sm text-red-600">Error: {errors}</div>', status=400)
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


# -------------------------
# Cambiar estado (htmx-friendly)
# -------------------------
@login_required
@require_POST
def cambiar_estado(request, pk):
    reclamo = get_object_or_404(Reclamo, pk=pk)
    if not (request.user.is_staff or es_agent(request.user)):
        return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)

    nuevo_estado = request.POST.get('nuevo_estado')
    nota = request.POST.get('nota', '')
    asignado_id = request.POST.get('asignado_a')

    if not nuevo_estado:
        return JsonResponse({'ok': False, 'error': 'nuevo_estado es requerido'}, status=400)

    estados_permitidos = [e[0] for e in Reclamo._meta.get_field('estado').choices]
    if nuevo_estado not in estados_permitidos:
        return JsonResponse({'ok': False, 'error': 'Estado inválido'}, status=400)

    with transaction.atomic():
        if asignado_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                agente = User.objects.get(pk=int(asignado_id))
                reclamo.asignado_a = agente
            except Exception:
                return JsonResponse({'ok': False, 'error': 'agente inválido'}, status=400)

        reclamo.estado = nuevo_estado
        reclamo.save()

        HistorialEstado.objects.create(
            reclamo=reclamo,
            estado=nuevo_estado,
            nota=nota or f'Estado cambiado a {nuevo_estado} por {request.user.username}',
            usuario=request.user
        )

        if Interaccion:
            try:
                Interaccion.objects.create(
                    cliente=reclamo.cliente,
                    poliza=reclamo.poliza,
                    agente=request.user if hasattr(Interaccion, 'agente') else None,
                    tipo='LL' if es_agent(request.user) else 'EM',
                    nota=f"Estado cambiado a {nuevo_estado}. Nota: {nota[:500]}",
                    estado='PE' if hasattr(Interaccion, 'estado') and nuevo_estado in ['PENDIENTE', 'EN_PROCESO'] else ('RE' if hasattr(Interaccion, 'estado') else None)
                )
            except Exception:
                pass

    if es_hx_request(request):
        # retornamos pequeño fragmento para htmx (puedes personalizar)
        return HttpResponse(f'<div class="text-sm text-green-600">Estado actualizado a {reclamo.get_estado_display()}.</div>')
    return JsonResponse({'ok': True, 'nuevo_estado': nuevo_estado})


# -------------------------
# JSON / endpoint para tarjetas
# -------------------------
@login_required
@require_GET
def reclamos_json_recientes(request):
    try:
        n = int(request.GET.get('n', 5))
    except (ValueError, TypeError):
        n = 5

    reclamos_qs = Reclamo.objects.filter(cliente=request.user).select_related('poliza').order_by('-fecha')[:n]

    # Si es htmx, retornamos fragmento HTML con las tarjetas (más cómodo para hx-swap)
    if es_hx_request(request):
        # render partial and return HTML (load template that renders cards)
        from django.template.loader import render_to_string
        html = render_to_string('reclamos/partials/_tarjetas_recientes.html', {'reclamos': reclamos_qs, 'user': request.user})
        return HttpResponse(html)

    lista = []
    for r in reclamos_qs:
        resumen = (r.descripcion[:200] + '...') if len(r.descripcion) > 200 else r.descripcion
        lista.append({
            'id': r.id,
            'codigo': r.codigo,
            'poliza_tipo': r.poliza.get_tipo_display() if r.poliza else '',
            'poliza_numero': getattr(r.poliza, 'poliza_numero', ''),
            'resumen': resumen,
            'estado': r.estado,
            'estado_display': r.get_estado_display(),
            'prioridad': r.prioridad,
            'fecha': timezone.localtime(r.fecha).strftime('%d/%m/%Y %H:%M'),
            'evidencia_url': r.evidencia.url if r.evidencia else '',
            'detalle_url': request.build_absolute_uri(r.get_absolute_url())
        })

    return JsonResponse({'reclamos': lista}, encoder=DjangoJSONEncoder)
