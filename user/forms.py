from django import forms
from .models import CustomUser, Role
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "Contraseña actual"
        self.fields["new_password1"].label = "Nueva contraseña"
        self.fields["new_password1"].help_text = (
            "Tu contraseña no puede ser similar a otra información personal."
            " Debe contener al menos 8 caracteres."
            " No debe ser una contraseña común ni completamente numérica."
        )
        self.fields["new_password2"].label = "Confirmar nueva contraseña"


class RoleAssignmentForm(forms.ModelForm):
    """
    Formulario para asignar roles a un usuario.

    Este formulario permite seleccionar múltiples roles para un usuario utilizando un conjunto de checkboxes.

    Attributes:
        roles (ModelMultipleChoiceField): Campo para seleccionar múltiples roles, representado como checkboxes.

    Meta:
        model (CustomUser): El modelo `CustomUser` asociado con este formulario.
        fields (list): Los campos del modelo que se incluyen en el formulario (en este caso, solo 'roles').
    """

    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(), widget=forms.CheckboxSelectMultiple, required=True
    )

    class Meta:
        model = CustomUser
        fields = ["roles"]


# form que el usuario debe completar para poder registrarse
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "phone"]  # Adjust fields as needed
        exclude = ["email"]
        labels = {
            "username": "Nombre de usuario",
            "phone": "Teléfono",
        }
        help_texts = {
            "username": "Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.",
            "phone": "Ingresa tu número de teléfono.",
        }
