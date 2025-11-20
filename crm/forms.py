from django import forms
from .models import Interaccion

class InteraccionForm(forms.ModelForm):
    class Meta:
        model = Interaccion
        fields = ['cliente', 'agente', 'poliza', 'tipo', 'nota', 'estado']
        widgets = {
            'nota': forms.Textarea(attrs={'rows': 3}),
        }
