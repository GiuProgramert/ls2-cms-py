from django import forms
from .models import CustomUser, Role
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Formulario personalizado para el cambio de contraseña.

    Este formulario permite al usuario cambiar su contraseña. Modifica las etiquetas y los textos de ayuda de los campos relacionados con la contraseña.

    Attributes:
        old_password (CharField): Campo para la contraseña actual.
        new_password1 (CharField): Campo para la nueva contraseña, incluye reglas como un mínimo de 8 caracteres.
        new_password2 (CharField): Campo para confirmar la nueva contraseña.
    """

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


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado para la creación de un nuevo usuario.

    Este formulario extiende `UserCreationForm` y agrega un campo de correo electrónico requerido.

    Attributes:
        email (EmailField): Campo de correo electrónico requerido.

    Meta:
        model (CustomUser): El modelo `CustomUser` asociado con este formulario.
        fields (tuple): Los campos del modelo que se incluyen en el formulario ('username', 'email', 'password1', 'password2').
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        """
        Sobrescribe el método `save` para asegurar que el correo electrónico del usuario
        se guarde correctamente.

        Args:
            commit (bool): Define si se debe guardar el usuario inmediatamente o no.

        Returns:
            CustomUser: El usuario creado o modificado.
        """
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """
    Formulario para actualizar el perfil de un usuario.

    Este formulario permite la edición de los campos 'username' y 'phone', excluyendo el correo electrónico.

    Meta:
        model (CustomUser): El modelo `CustomUser` asociado con este formulario.
        fields (list): Los campos del modelo que se incluyen en el formulario ('username', 'phone').
        exclude (list): Campos excluidos en el formulario (en este caso 'email').
        labels (dict): Etiquetas personalizadas para los campos.
        help_texts (dict): Textos de ayuda personalizados para los campos.
    """

    class Meta:
        model = CustomUser
        fields = ["username", "phone"]  # Ajusta los campos según sea necesario
        exclude = ["email"]
        labels = {
            "username": "Nombre de usuario",
            "phone": "Teléfono",
        }
        help_texts = {
            "username": "Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.",
            "phone": "Ingresa tu número de teléfono.",
        }


class UserSearchForm(forms.Form):
    """
    Formulario para buscar y filtrar usuarios.

    Campos:
        search_term (CharField): Campo de texto opcional para ingresar el término de búsqueda por nombre o email.
        order_by (ChoiceField): Campo de selección que permite ordenar los resultados por nombre o fecha de creación.
        filter_role (ChoiceField): Campo de selección dinámico que se llena con los roles existentes en el sistema.
    """

    search_term = forms.CharField(
        max_length=255,
        required=False,
        label="Buscar usuario",
        widget=forms.TextInput(
            attrs={"placeholder": "Ingrese el nombre o email del usuario"}
        ),
    )

    filter_role = forms.ChoiceField(
        required=False, label="Filtrar por rol", widget=forms.Select
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Poblar dinámicamente el campo filter_role con los roles existentes
        roles = Role.objects.all()
        role_choices = [("all", "Todos")] + [
            (role.name, role.name) for role in roles
        ]  # 'all' es la opción por defecto
        self.fields["filter_role"].choices = role_choices
