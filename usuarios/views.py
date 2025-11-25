import os
import uuid
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import PerfilForm, RegistroForm
from .models import Perfil
from polizas.models import ProductoPoliza
from django.conf import settings
from reclamos.models import Reclamo
from crm.models import Interaccion


# =========================================================
#    FUNCIONES DE VERIFICACIÓN DE ROLES
# =========================================================

def es_cliente(user):
    """Usuario normal (no staff, no superuser)."""
    return not user.is_staff and not user.is_superuser


def es_administrador(user):
    """Usuario con permisos administrativos."""
    return user.is_staff or user.is_superuser


# =========================================================
#    VISTAS PÚBLICAS
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
                return redirect('inicio_administrador')
            else:
                return redirect('inicio_cliente')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'usuarios/login.html')


def logout_view(request):
    """Cerrar sesión."""
    logout(request)
    return redirect('login')


def registro(request):
    """Registro de usuarios nuevos."""
    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect('login')
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {"form": form})


# =========================================================
#    VISTAS PROTEGIDAS POR ROL (CLIENTE)
# =========================================================

# Función que comprueba que el usuario sea cliente
def es_cliente(user):
    try:
        return user.perfil.rol == 'client'
    except Exception:
        return False

@login_required
@user_passes_test(es_cliente, login_url='/no-autorizado/')
def inicio_cliente(request):
    perfil = request.user.perfil
    polizas = request.user.polizas.all()

    polizas_activas = polizas.filter(estado='ACTIVA').count()
    pagos_pendientes = sum(p.saldo_pendiente() for p in polizas)
    cotizaciones = request.user.cotizaciones.count()

    productos_disponibles = ProductoPoliza.objects.filter(disponible=True)

    # 🔹 Reclamos recientes del cliente (últimos 5)
    reclamos_recientes = Reclamo.objects.filter(cliente=request.user).order_by('-fecha')[:5]

    # 🔹 Última interacción del CRM relacionada con las pólizas del usuario
    ultima_interaccion = Interaccion.objects.filter(cliente=request.user).order_by('-fecha_creacion').first()

    return render(request, 'cliente/inicio_cliente.html', {
        'perfil': perfil,
        'polizas_activas': polizas_activas,
        'pagos_pendientes': pagos_pendientes,
        'cotizaciones': cotizaciones,
        'productos_disponibles': productos_disponibles,
        'reclamos_recientes': reclamos_recientes,
        'ultima_interaccion': ultima_interaccion,  # 🔹 Pasamos solo 1
    })


# =========================================================
#    VISTAS PROTEGIDAS POR ROL (ADMIN)
# =========================================================

@login_required
@user_passes_test(es_administrador, login_url='/no-autorizado/')
def inicio_admin(request):
    return render(request, 'administrador/inicio_admin.html')

@login_required
def descargar_documento(request, perfil_id):
    try:
        perfil = Perfil.objects.get(id=perfil_id)
    except Perfil.DoesNotExist:
        raise Http404("Perfil no encontrado")

    # Validación de acceso: solo el dueño o admin
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


# =========================================================
#    PERFIL DEL USUARIO
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
            return redirect('perfil')

    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'cliente/editar_perfil.html', {'form': form})



