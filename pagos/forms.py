from django import forms
from .models import Pago

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['aseguradora', 'monto', 'metodo', 'referencia', 'comprobante', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Información adicional...'}),
            'monto': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }
