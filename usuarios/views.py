from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


# Vista de inicio general
def inicio(request):
    return render(request, 'usuarios/base.html')


# Vista inicio para clientes (usuarios normales)
@login_required
def inicio_cliente(request):
    return render(request, 'cliente/inicio_cliente.html')


# Vista inicio para administradores (solo para usuarios staff o superuser)
@login_required
def inicio_admin(request):
    return render(request, 'administrador/inicio_admin.html')


# Vista de login general
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Redirigir según tipo de usuario
            if user.is_staff or user.is_superuser:
                return redirect('inicio_administrador')  # Redirección a la vista admin
            else:
                return redirect('inicio_cliente')        # Redirección a la vista cliente
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'usuarios/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def registro(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Usuario creado correctamente')
        return redirect('login')
    return render(request, 'usuarios/registro.html')
