from django.shortcuts import render
from django.http import HttpResponse
from .models import ChatMessage 
from django.views.decorators.http import require_http_methods
import time

# Helper para obtener o crear la clave de sesión
def get_session_key(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key

# Lógica básica de respuesta (puedes expandirla o reemplazarla con un LLM)
def get_bot_response(user_message):
    user_message = user_message.lower().strip()
    
    if any(word in user_message for word in ["hola", "saludo"]):
        return "¡Bienvenido! Soy tu asistente de seguros. ¿Necesitas una cotización o tienes preguntas sobre reclamos?"
    elif any(word in user_message for word in ["cotizar", "precio"]):
        return "Para cotizar, dime qué quieres asegurar (Carro, Casa, Negocio, Familia)."
    # ... otras reglas ...
    else:
        return "Nuestras áreas principales son Carro, Casa, Negocio y Familia. Te recomiendo contactar a un agente."

# 1. VISTA para ENVIAR MENSAJE (POST)
@require_http_methods(["POST"])
def send_message(request):
    """Recibe el mensaje del usuario por HTMX, genera respuesta y guarda en DB."""
    user_message = request.POST.get('user_message', '')
    
    if not user_message:
        return HttpResponse(status=204) # No content
    
    time.sleep(1) # Simula tiempo de respuesta
    
    bot_response = get_bot_response(user_message)
    session_key = get_session_key(request)

    ChatMessage.objects.create(
        session_key=session_key,
        message=user_message,
        response=bot_response
    )
    
    # Renderiza la plantilla parcial para HTMX
    context = {
        'user_message': user_message,
        'bot_response': bot_response,
    }
    return render(request, 'includes/message_response.html', context)

# 2. VISTA para CARGAR HISTORIAL (GET)
@require_http_methods(["GET"])
def load_history(request):
    """Carga el historial de mensajes para la sesión actual."""
    session_key = get_session_key(request)
    messages = ChatMessage.objects.filter(session_key=session_key).order_by('timestamp')
    
    context = {
        'messages': messages,
    }
    # Renderiza la plantilla del historial
    return render(request, 'includes/chat_history.html', context)