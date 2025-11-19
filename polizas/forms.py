# forms.py
from django import forms
from .models import ProductoPoliza
from usuarios.forms import validar_documento


class AdquirirPolizaForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=ProductoPoliza.objects.filter(disponible=True),
        empty_label="Selecciona una póliza"
    )
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    documento_id = forms.FileField(required=False, validators=[validar_documento])
    cobertura_extra = forms.MultipleChoiceField(
        choices=[('ambulancia','Ambulancia'),('hospitalizacion','Hospitalización')],
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
