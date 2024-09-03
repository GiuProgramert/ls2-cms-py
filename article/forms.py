from django import forms
from article.models import Category


class CategoryForm(forms.ModelForm):
    """
    Formulario para la creación y edición de instancias del modelo `Category`.

    Esta clase utiliza `forms.ModelForm` para generar un formulario basado en el modelo `Category`.
    Los campos incluidos en el formulario son: 'name', 'description', 'type', 'state', e 'is_moderated'.
    
    Attributes:
        Meta (class): Clase interna que define las opciones del formulario.
            model (Model): Modelo en el que se basa el formulario.
            fields (list): Lista de campos del modelo que se incluirán en el formulario.
            labels (dict): Diccionario que proporciona etiquetas personalizadas para los campos del formulario.
    """

    class Meta:
        model = Category
        fields = ["name", "description", "type", "state", "is_moderated"]

        labels = {
            "name": "Nombre",
            "description": "Descripción",
            "type": "Tipo",
            "state": "Estado",
            "is_moderated": "Moderado",
        }
