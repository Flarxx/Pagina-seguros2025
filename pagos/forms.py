from django import forms
from .models import Pago, EmpresaAseguradora

# Opciones de ejemplo para método de pago
METODOS_PAGO = [
    ('Transferencia', 'Transferencia'),
    ('Pago móvil', 'Pago móvil'),
    ('Efectivo', 'Efectivo'),
]

class PagoForm(forms.ModelForm):
    # Sobrescribir los campos para agregar opciones de prueba
    metodo = forms.ChoiceField(choices=METODOS_PAGO, widget=forms.Select(
        attrs={'class': 'w-full border border-purple-300 rounded-lg p-3 focus:ring-2 focus:ring-purple-500 focus:border-purple-500'}
    ))
    aseguradora = forms.ModelChoiceField(
        queryset=EmpresaAseguradora.objects.all(),
        empty_label="Selecciona aseguradora",
        widget=forms.Select(
            attrs={'class': 'w-full border border-purple-300 rounded-lg p-3 focus:ring-2 focus:ring-purple-500 focus:border-purple-500'}
        )
    )

    class Meta:
        model = Pago
        fields = ['aseguradora', 'monto', 'metodo', 'referencia', 'comprobante', 'observaciones']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'w-full border border-purple-300 rounded-lg p-3 focus:ring-2 focus:ring-purple-500 focus:border-purple-500'}),
            'referencia': forms.TextInput(attrs={'class': 'w-full border border-purple-300 rounded-lg p-3 focus:ring-2 focus:ring-purple-500 focus:border-purple-500'}),
            'comprobante': forms.ClearableFileInput(attrs={'class': 'w-full border border-purple-300 rounded-lg p-3 focus:ring-2 focus:ring-purple-500 focus:border-purple-500'}),
            'observaciones': forms.Textarea(attrs={'class': 'w-full border border-purple-300 rounded-lg p-3 focus:ring-2 focus:ring-purple-500 focus:border-purple-500', 'rows': 3}),
        }
