# reclamos/forms.py
from django import forms
from .models import Reclamo, ESTADOS, PRIORIDADES


class ReclamoClienteForm(forms.ModelForm):
    class Meta:
        model = Reclamo
        fields = ['poliza', 'motivo', 'descripcion', 'prioridad', 'evidencia']
        widgets = {
            'motivo': forms.TextInput(attrs={'class': 'block w-full border rounded px-2 py-1'}),
            'descripcion': forms.Textarea(attrs={'class': 'block w-full border rounded px-2 py-1', 'rows': 4}),
            'prioridad': forms.Select(attrs={'class': 'block w-full border rounded px-2 py-1'}),
            'poliza': forms.Select(attrs={'class': 'block w-full border rounded px-2 py-1'}),
        }

    def clean_descripcion(self):
        desc = self.cleaned_data.get('descripcion', '') or ''
        if len(desc.strip()) < 20:
            raise forms.ValidationError("Describe el reclamo con al menos 20 caracteres.")
        return desc


class ReclamoStaffForm(forms.ModelForm):
    class Meta:
        model = Reclamo
        fields = ['motivo', 'descripcion', 'prioridad', 'estado', 'asignado_a']
        widgets = {
            'motivo': forms.TextInput(attrs={'class': 'block w-full border rounded px-2 py-1'}),
            'descripcion': forms.Textarea(attrs={'class': 'block w-full border rounded px-2 py-1', 'rows': 4}),
            'prioridad': forms.Select(attrs={'class': 'block w-full border rounded px-2 py-1'}),
            'estado': forms.Select(attrs={'class': 'block w-full border rounded px-2 py-1'}),
            'asignado_a': forms.Select(attrs={'class': 'block w-full border rounded px-2 py-1'}),
        }

    def clean(self):
        cleaned = super().clean()
        # Aquí puedes añadir validaciones de negocio si quieres
        return cleaned


class EvidenciaForm(forms.ModelForm):
    class Meta:
        model = Reclamo
        fields = ['evidencia']
        widgets = {
            'evidencia': forms.ClearableFileInput(attrs={'class': 'block w-full'}),
        }

    def clean_evidencia(self):
        archivo = self.cleaned_data.get('evidencia')
        # Los validadores del modelo ya cubren extensión y tamaño,
        # pero los repetimos para dar feedback en el form.
        if archivo:
            ext = archivo.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'pdf']:
                raise forms.ValidationError("Solo se permiten JPG, PNG o PDF.")
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError("El archivo no puede superar los 10 MB.")
        else:
            raise forms.ValidationError("Selecciona un archivo.")
        return archivo


class CambiarEstadoForm(forms.Form):
    estado = forms.ChoiceField(choices=ESTADOS, widget=forms.Select(attrs={'class': 'block w-full'}))
    nota = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'block w-full'}))
