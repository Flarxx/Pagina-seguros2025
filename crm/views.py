from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Interaccion
from .forms import InteraccionForm
from django.contrib import messages
from django.http import JsonResponse

# Lista todas las interacciones visibles para el usuario
@login_required
def lista_interacciones(request):
    user = request.user
    if user.is_staff:
        interacciones = Interaccion.objects.all().order_by('-fecha_creacion')
    elif hasattr(user, 'perfil') and user.perfil.rol == 'agent':
        interacciones = Interaccion.objects.filter(agente=user).order_by('-fecha_creacion')
    else:  # cliente
        interacciones = Interaccion.objects.filter(cliente=user).order_by('-fecha_creacion')

    return render(request, 'crm/lista_interacciones.html', {'interacciones': interacciones})


@login_required
def detalle_interaccion(request, pk):
    interaccion = get_object_or_404(Interaccion, pk=pk)

    # Permisos: solo admin, cliente o agente asignado
    if not (request.user.is_staff or interaccion.cliente == request.user or interaccion.agente == request.user):
        messages.error(request, "No tienes permisos para ver esta interacción")
        return redirect('crm:lista_interacciones')

    return render(request, 'crm/detalle_interaccion.html', {'interaccion': interaccion})


@login_required
def crear_interaccion(request):
    if request.method == 'POST':
        form = InteraccionForm(request.POST)
        if form.is_valid():
            interaccion = form.save(commit=False)
            # Para clientes, asignar automáticamente
            if not request.user.is_staff and hasattr(request.user, 'perfil') and request.user.perfil.rol != 'agent':
                interaccion.cliente = request.user
            interaccion.save()
            messages.success(request, "Interacción creada correctamente")
            return redirect('crm:lista_interacciones')
    else:
        form = InteraccionForm()

    return render(request, 'crm/crear_interaccion.html', {'form': form})


@login_required
def editar_interaccion(request, pk):
    interaccion = get_object_or_404(Interaccion, pk=pk)

    if not (request.user.is_staff or interaccion.agente == request.user):
        messages.error(request, "No tienes permisos para editar esta interacción")
        return redirect('crm:lista_interacciones')

    if request.method == 'POST':
        form = InteraccionForm(request.POST, instance=interaccion)
        if form.is_valid():
            form.save()
            messages.success(request, "Interacción actualizada correctamente")
            return redirect('crm:detalle_interaccion', pk=pk)
    else:
        form = InteraccionForm(instance=interaccion)

    return render(request, 'crm/editar_interaccion.html', {'form': form, 'interaccion': interaccion})

@login_required
def interacciones_recientes_cliente(request):
    interacciones = Interaccion.objects.filter(cliente=request.user).order_by('-fecha_creacion')[:5]

    data = []

    for inter in interacciones:
        data.append({
            'tipo': inter.tipo,
            'nota': inter.nota,  # ← cambiar 'descripcion' por 'nota'
            'estado': inter.estado,
            'fecha': inter.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
        })

    return JsonResponse({'interacciones': data})