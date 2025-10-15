from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import PerfilForm

# ----------------------------
# Funciones de verificación de rol
# ----------------------------
def es_cliente(user):
    # Usuario que no es staff ni superuser
    return not user.is_staff and not user.is_superuser

def es_administrador(user):
    # Usuario staff o superuser
    return user.is_staff or user.is_superuser

# ----------------------------
# Vistas públicas
# ----------------------------
def inicio(request):    
    """Página de inicio general"""
    return render(request, 'usuarios/inicio.html')

def login_view(request):
    """Login general con redirección según rol"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Redirigir según tipo de usuario
            if es_administrador(user):
                return redirect('inicio_administrador')
            else:
                return redirect('inicio_cliente')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'usuarios/login.html')

def logout_view(request):
    """Cerrar sesión"""
    logout(request)
    return redirect('login')

def registro(request):
    """Registro de nuevos usuarios"""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Usuario creado correctamente')
        return redirect('login')
    return render(request, 'usuarios/registro.html')

# ----------------------------
# Vistas protegidas por rol
# ----------------------------
@login_required
@user_passes_test(es_cliente, login_url='/no-autorizado/')
def inicio_cliente(request):
    """Inicio para clientes normales"""
    return render(request, 'cliente/inicio_cliente.html')

@login_required
@user_passes_test(es_administrador, login_url='/no-autorizado/')
def inicio_admin(request):
    """Inicio para administradores"""
    return render(request, 'administrador/inicio_admin.html')


# vista para que el usuario maneje su propia informacion 


@login_required
def perfil(request):
    perfil = request.user.perfil
    return render(request, 'usuarios/perfil.html', {'perfil': perfil})


@login_required
def editar_perfil(request):
    perfil = request.user.perfil
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = PerfilForm(instance=perfil)
    return render(request, 'usuarios/editar_perfil.html', {'form': form})