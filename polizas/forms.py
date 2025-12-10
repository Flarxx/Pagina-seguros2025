# polizas/forms.py
from django import forms
from django.utils import timezone
from .models import ProductoPoliza
from usuarios.forms import validar_documento  # asegúrate que existe y está accesible


class AdquirirPolizaForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=ProductoPoliza.objects.filter(disponible=True),
        empty_label="Selecciona una póliza",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        help_text="Seleccione la fecha de inicio (hoy o futuro)."
    )

    documento_id = forms.FileField(
        required=False,
        validators=[validar_documento],
        widget=forms.ClearableFileInput(attrs={'class': 'form-input'})
    )

    cobertura_extra = forms.MultipleChoiceField(
        choices=[('ambulancia', 'Ambulancia'), ('hospitalizacion', 'Hospitalización')],
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Seleccione coberturas adicionales si las desea."
    )

    def clean_fecha_inicio(self):
        fecha = self.cleaned_data.get('fecha_inicio')
        if fecha and fecha < timezone.now().date():
            raise forms.ValidationError("La fecha de inicio no puede ser anterior a hoy.")
        return fecha


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
        required=False,  # Opcional si num_dependientes_adultos es 0
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
    edad_promedio_hijos = forms.IntegerField(
        label='Edad del Hijo Mayor',
        required=False,
        min_value=0,
        max_value=17,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 7 (si aplica)'})
    )

    def clean(self):
        cleaned_data = super().clean()

        num_adultos = cleaned_data.get("num_dependientes_adultos")
        edad_adulto = cleaned_data.get("edad_dependiente_adulto")

        num_hijos = cleaned_data.get("num_hijos")
        edad_hijo = cleaned_data.get("edad_promedio_hijos")

        # Validación: si existe 1 dependiente adulto, su edad es obligatoria
        if num_adultos == 1 and not edad_adulto:
            self.add_error(
                "edad_dependiente_adulto",
                "Debes indicar la edad del dependiente adulto."
            )

        # Validación: si hay hijos > 0, edad del hijo mayor obligatoria
        if num_hijos and num_hijos > 0 and (edad_hijo is None):
            self.add_error(
                "edad_promedio_hijos",
                "Debes indicar la edad del hijo mayor cuando indicas número de hijos."
            )

        # Validación extra: si edad_promedio_hijos está dada, asegurar que num_hijos > 0
        if edad_hijo and (num_hijos == 0 or num_hijos is None):
            self.add_error(
                "num_hijos",
                "Indica el número de hijos si proporcionas la edad del hijo mayor."
            )

        return cleaned_data
