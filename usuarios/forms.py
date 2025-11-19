from django import forms
from .models import Perfil
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# ---------------------------
# VALIDACIÓN SEGURA DEL ARCHIVO
# ---------------------------
def validar_documento(value):
    max_size = 5 * 1024 * 1024  # 5 MB
    if value.size > max_size:
        raise ValidationError("El archivo no puede superar los 5 MB.")

    tipos_permitidos = ['application/pdf', 'image/jpeg', 'image/png']
    if value.content_type not in tipos_permitidos:
        raise ValidationError("Solo se permiten PDF, JPG o PNG.")

# ---------------------------
# FORMULARIO DEL PERFIL
# ---------------------------
class PerfilForm(forms.ModelForm):
    documento_id = forms.FileField(
        required=False,
        validators=[validar_documento],
        widget=forms.FileInput(attrs={'class': 'border p-2 rounded w-full'})
    )

    class Meta:
        model = Perfil
        fields = ['cedula', 'telefono', 'direccion', 'fecha_nacimiento', 'documento_id']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

# ---------------------------
# REGISTRO DE USUARIO
# ---------------------------
class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email
