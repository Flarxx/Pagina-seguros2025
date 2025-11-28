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




class PerfilFamiliarForm(forms.Form):
    """Formulario para capturar los datos necesarios para cotizar la prima."""
    
    # 1. Datos del Titular (Mínimo requerido)
    edad_titular = forms.IntegerField(
        label='Edad del Titular',
        min_value=18,
        max_value=75,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 35'})
    )

    # 2. Datos de la Familia
    num_dependientes_adultos = forms.IntegerField(
        label='Número de Dependientes Adultos (Esposa/Pareja)',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0 o 1'})
    )

    edad_dependiente_adulto = forms.IntegerField(
        label='Edad del Dependiente Adulto',
        required=False, # Opcional si num_dependientes_adultos es 0
        min_value=18,
        max_value=75,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 33 (si aplica)'})
    )

    num_hijos = forms.IntegerField(
        label='Número de Hijos (Menores de 18)',
        min_value=0,
        max_value=5,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 2'})
    )

    # Nota: Simplificamos asumiendo que todos los hijos tienen una edad promedio o la edad del mayor hijo es suficiente.
    # Para ser más precisos, se requeriría un formulario dinámico que pida la edad de cada hijo.
    edad_promedio_hijos = forms.IntegerField(
        label='Edad del Hijo Mayor',
        required=False,
        min_value=0,
        max_value=17,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 7 (si aplica)'})
    )
