import os
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.conf import settings

from django.db.models import Prefetch, Q
from django.contrib.auth import get_user_model

from .forms import PerfilForm, RegistroForm
from .models import Perfil

from polizas.models import ProductoPoliza, Poliza
from reclamos.models import Reclamo
from crm.models import Interaccion


# =========================================================
# FUNCIONES DE VERIFICACIÓN DE ROLES
# =========================================================

def es_cliente(user):
    """Usuario normal (no staff, no superuser)."""
    try:
        return user.perfil.rol == 'client'
    except Exception:
        return False


def es_administrador(user):
    """Usuario con permisos administrativos."""
    return user.is_staff or user.is_superuser


# =========================================================
# VISTAS PÚBLICAS
# =========================================================

def inicio(request):
    """Página de inicio pública general."""
    opciones_seguro = [
        ('carro', 'Mi carro'),
        ('familia', 'Mi familia'),
        ('tienda', 'Mi negocio'),
        ('casa', 'Mi casa'),
    ]
    return render(request, 'usuarios/inicio.html', {'opciones_seguro': opciones_seguro})


def login_view(request):
    """Login general con redirección según rol."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if es_administrador(user):
                return redirect('usuarios:inicio_administrador')
            else:
                return redirect('usuarios:inicio_cliente')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'usuarios/login.html')


def logout_view(request):
    """Cerrar sesión."""
    logout(request)
    return redirect('usuarios:login')


def registro(request):
    """Registro de usuarios nuevos."""
    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect('usuarios:login')
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {"form": form})


# =========================================================
# VISTAS PROTEGIDAS POR ROL (CLIENTE)
# =========================================================

@login_required
@user_passes_test(es_cliente, login_url='/no-autorizado/')
def inicio_cliente(request):
    perfil = request.user.perfil
    polizas = request.user.polizas.all()

    polizas_activas = polizas.filter(estado='ACTIVA').count()
    pagos_pendientes = sum(p.saldo_pendiente() for p in polizas)
    cotizaciones = request.user.cotizaciones.count()

    productos_disponibles = ProductoPoliza.objects.filter(disponible=True)

    reclamos_recientes = Reclamo.objects.filter(cliente=request.user).order_by('-fecha')[:5]

    ultima_interaccion = Interaccion.objects.filter(cliente=request.user).order_by('-fecha_creacion').first()

    return render(request, 'cliente/inicio_cliente.html', {
        'perfil': perfil,
        'polizas_activas': polizas_activas,
        'pagos_pendientes': pagos_pendientes,
        'cotizaciones': cotizaciones,
        'productos_disponibles': productos_disponibles,
        'reclamos_recientes': reclamos_recientes,
        'ultima_interaccion': ultima_interaccion,
    })


# =========================================================
# VISTAS PROTEGIDAS POR ROL (ADMIN)
# =========================================================

@login_required
@user_passes_test(es_administrador, login_url='/no-autorizado/')
def inicio_admin(request):
    return render(request, 'administrador/inicio_admin.html')


@login_required
def descargar_documento(request, perfil_id):
    perfil = get_object_or_404(Perfil, id=perfil_id)

    if request.user != perfil.usuario and not request.user.is_staff:
        return HttpResponse("No autorizado", status=403)

    if not perfil.documento_id:
        return HttpResponse("Documento no disponible", status=404)

    ruta_archivo = perfil.documento_id.path
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(ruta_archivo)}"'
            return response
    else:
        return HttpResponse("Archivo no encontrado", status=404)


@login_required
@user_passes_test(lambda u: u.is_staff)
def control_clientes(request):
    q = request.GET.get('q', '').strip()

    perfiles_qs = Perfil.objects.select_related('usuario')

    if q:
        perfiles_qs = perfiles_qs.filter(
            Q(cedula__icontains=q) |
            Q(usuario__username__icontains=q) |
            Q(usuario__first_name__icontains=q) |
            Q(usuario__last_name__icontains=q) |
            Q(usuario__email__icontains=q)
        )

    perfiles_qs = perfiles_qs.prefetch_related(
        Prefetch('usuario__polizas', queryset=Poliza.objects.prefetch_related('pagos')),
        Prefetch('usuario__reclamo_set', queryset=Reclamo.objects.only('id', 'estado'))
    ).order_by('-id')

    paginator = Paginator(perfiles_qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    clientes = []

    for perfil in page_obj.object_list:
        user = perfil.usuario

        polizas = list(user.polizas.all())
        polizas_count = len(polizas)

        pagos_pendientes_total = 0
        for pol in polizas:
            for pago in getattr(pol, 'pagos', []):
                if pago.estado_pago == 'pendiente':
                    pagos_pendientes_total += pago.monto or 0

        reclamos_abiertos = sum(
            1 for r in getattr(user, 'reclamo_set', []).all()
            if r.estado in ['PENDIENTE', 'EN_PROCESO']
        )

        clientes.append({
            'perfil': perfil,
            'user': user,
            'polizas_count': polizas_count,
            'pagos_pendientes_total': pagos_pendientes_total,
            'reclamos_abiertos': reclamos_abiertos,
        })

    context = {
        'clientes': clientes,
        'page_obj': page_obj,
        'q': q,
    }

    return render(request, 'administrador/control_clientes.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def detalle_cliente_admin(request, cliente_id):
    usuario = get_object_or_404(User, id=cliente_id)
    perfil = get_object_or_404(Perfil, usuario=usuario)

    polizas = Poliza.objects.filter(cliente=usuario).prefetch_related('pagos')
    reclamos = Reclamo.objects.filter(cliente=usuario).order_by('-fecha')

    pagos_pendientes = 0
    pagos_aprobados = 0

    for pol in polizas:
        for pago in pol.pagos.all():
            if pago.estado_pago == 'pendiente':
                pagos_pendientes += pago.monto or 0
            elif pago.estado_pago == 'aprobado':
                pagos_aprobados += pago.monto or 0

    context = {
        'usuario': usuario,
        'perfil': perfil,
        'polizas': polizas,
        'reclamos': reclamos,
        'pagos_pendientes': pagos_pendientes,
        'pagos_aprobados': pagos_aprobados,
    }

    return render(request, 'administrador/detalle_cliente.html', context)


# =========================================================
# PERFIL DEL USUARIO
# =========================================================

@login_required
def perfil(request):
    perfil = request.user.perfil
    return render(request, 'cliente/perfil.html', {'perfil': perfil})


@login_required
def editar_perfil(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)

        if form.is_valid():

            archivo = request.FILES.get('documento_id')

            if archivo:
                # 1. Generar nombre único
                ext = archivo.name.split('.')[-1]
                nombre_seguro = f"{uuid.uuid4()}.{ext}"

                # 2. Borrar archivo anterior
                if perfil.documento_id and default_storage.exists(perfil.documento_id.name):
                    default_storage.delete(perfil.documento_id.name)

                # 3. Guardar archivo seguro
                ruta = os.path.join("documentos", nombre_seguro)
                default_storage.save(ruta, ContentFile(archivo.read()))

                # 4. Asignar archivo
                perfil.documento_id = ruta

            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('usuarios:perfil')

    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'cliente/editar_perfil.html', {'form': form})
