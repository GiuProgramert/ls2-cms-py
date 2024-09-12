from django import forms
from roles.models import Role, Permission

class RoleForm(forms.ModelForm):
    """
    Formulario para la creación y edición de roles.

    Este formulario permite la creación o modificación de un rol dentro del sistema,
    proporcionando campos para el nombre, descripción y los permisos asociados al rol.

    Attributes:
        Meta (class): Clase que define el modelo asociado al formulario y los campos que se utilizarán.
            - model (Role): Modelo de base asociado al formulario.
            - fields (list): Lista de campos del modelo `Role` que serán incluidos en el formulario.
        permissions (ModelMultipleChoiceField): Campo que permite seleccionar uno o más permisos
            mediante una lista de checkboxes. Este campo utiliza el conjunto de permisos disponibles 
            en el sistema (`Permission.objects.all()`) y es obligatorio.
        labels (dict): Diccionario que proporciona etiquetas personalizadas para los campos del formulario.
    """

    class Meta:
        model = Role
        fields = ['name', 'description', 'permissions']

    permissions = forms.ModelMultipleChoiceField(
        queryset = Permission.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        required = True,
        label = "Permisos"
    )

    labels = {
                "name": "Nombre",
                "description": "Descripción",
            }