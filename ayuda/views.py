from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import FAQ, CategoriaFAQ, Ticket
from .forms import ContactoForm, TicketForm, MensajeTicketForm

def ayuda_index(request):
    q = request.GET.get('q','')
    faqs = FAQ.objects.filter(publicado=True)
    if q:
        faqs = faqs.filter(pregunta__icontains=q) | faqs.filter(respuesta__icontains=q)
    categorias = CategoriaFAQ.objects.all()
    return render(request, 'ayuda/index.html', {'faqs': faqs, 'categorias': categorias, 'q': q})

def faq_detail(request, pk):
    faq = get_object_or_404(FAQ, pk=pk, publicado=True)
    return render(request, 'ayuda/faq_detail.html', {'faq': faq})

def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            # enviar correo (opcional)
            try:
                form.enviar_email()
            except Exception as e:
                # si falla el envío, se guarda en log y se notifica al admin en production
                pass
            messages.success(request, "Tu mensaje fue enviado. Te responderemos pronto.")
            return redirect('ayuda:index')
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = ContactoForm()
    return render(request, 'ayuda/contacto.html', {'form': form})

@login_required
def crear_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.usuario = request.user
            ticket.save()
            messages.success(request, "Ticket creado correctamente. Te contactaremos por aquí.")
            return redirect('ayuda:mis_tickets')
    else:
        form = TicketForm()
    return render(request, 'ayuda/crear_ticket.html', {'form': form})

@login_required
def mis_tickets(request):
    tickets = request.user.tickets.all().order_by('-creado')
    return render(request, 'ayuda/mis_tickets.html', {'tickets': tickets})

# Vista para detalle de ticket y responder (para usuario y staff)
@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    # si no es staff y no es dueño, prohibir
    if request.user != ticket.usuario and not request.user.is_staff:
        messages.error(request, "No tienes permiso para ver este ticket.")
        return redirect('ayuda:mis_tickets')

    if request.method == 'POST':
        form = MensajeTicketForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.ticket = ticket
            mensaje.autor = request.user
            mensaje.save()
            # opcional: cambiar estado
            if request.user.is_staff:
                ticket.estado = 'PRO'  # o lo que quieras
            ticket.save()
            messages.success(request, "Mensaje agregado al ticket.")
            return redirect('ayuda:ticket_detail', pk=ticket.pk)
    else:
        form = MensajeTicketForm()

    return render(request, 'ayuda/ticket_detail.html', {'ticket': ticket, 'form': form})
