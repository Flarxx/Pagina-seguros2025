# forms.py
from django import forms
from .models import ProductoPoliza

class AdquirirPolizaForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=ProductoPoliza.objects.filter(disponible=True),
        empty_label="Selecciona una póliza",
        widget=forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'})
    )
