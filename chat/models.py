from django.db import models

class ChatMessage(models.Model):
    # La clave de sesión para identificar la conversación
    session_key = models.CharField(max_length=40, db_index=True) 
    
    # El mensaje enviado por el usuario
    message = models.TextField()
    
    # La respuesta generada por el bot
    response = models.TextField()
    
    # Marca de tiempo
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
    # ... (método __str__ opcional)