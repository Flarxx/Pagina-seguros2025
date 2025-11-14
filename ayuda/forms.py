from django import forms
from .models import Ticket, MensajeTicket
from django.core.mail import send_mail
from django.conf import settings

class ContactoForm(forms.Form):
    nombre = forms.CharField(max_length=150)
    email = forms.EmailField()
    asunto = forms.CharField(max_length=200)
    mensaje = forms.CharField(widget=forms.Textarea)

    def enviar_email(self):
        cd = self.cleaned_data
        asunto = f"[Contacto] {cd['asunto']}"
        cuerpo = f"De: {cd['nombre']} <{cd['email']}>\n\n{cd['mensaje']}"
        send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['asunto', 'descripcion', 'prioridad']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows':4}),
        }

class MensajeTicketForm(forms.ModelForm):
    class Meta:
        model = MensajeTicket
        fields = ['mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows':3}),
        }
