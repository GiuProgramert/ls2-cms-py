from django import forms
from article.models import Category, Article
from mdeditor.fields import MDTextFormField
from taggit.forms import TagWidget
from taggit.models import Tag


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
        fields = ["name", "description", "type", "state", "is_moderated", "price"]

        labels = {
            "name": "Nombre",
            "description": "Descripción",
            "type": "Tipo",
            "state": "Estado",
            "is_moderated": "Moderado",
            "price": "Precio en Dolares",
        }


class ArticleForm(forms.ModelForm):
    """
    Formulario para la creación y edición de instancias del modelo `Article`.

    Esta clase utiliza `forms.ModelForm` para generar un formulario basado en el modelo `Article`.
    Los campos incluidos en el formulario son: 'title', 'description', 'category', y 'body'.

    Attributes:
        Meta (class): Clase interna que define las opciones del formulario.
            model (Model): Modelo en el que se basa el formulario.
            fields (list): Lista de campos del modelo que se incluirán en el formulario.
            labels (dict): Diccionario que proporciona etiquetas personalizadas para los campos del formulario.
    """

    body = MDTextFormField()

    class Meta:
        model = Article
        fields = ["title", "description", "category", "tags"]

        labels = {
            "title": "Titulo",
            "description": "Descripción",
            "body": "Cuerpo",
            "category": "Categoría",
        }
        widgets = {
            "tags": TagWidget(),
        }


class CategorySearchForm(forms.Form):
    """
    Formulario para buscar y filtrar categorías.

    Este formulario permite a los usuarios buscar categorías ingresando un término de búsqueda,
    así como filtrar y ordenar los resultados según los criterios seleccionados.

    Campos:
        search_term (CharField): Campo de texto opcional para ingresar el término de búsqueda por título.
        order_by (ChoiceField): Campo de selección que permite ordenar los resultados
                                por nombre o fecha de creación en orden ascendente o descendente.
        filter_type (ChoiceField): Campo de selección que permite filtrar las categorías por tipo
                                   (todos, gratis, suscripción o pago).
    """

    search_term = forms.CharField(
        max_length=255,
        required=False,
        label="Buscar categoría",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ingrese el título, descripción o tag de la categoría"
            }
        ),
    )
    order_by = forms.ChoiceField(
        choices=[("name", "A-Z"), ("-name", "Z-A")],
        required=False,
        label="Ordenar por",
        widget=forms.Select(attrs={"class": "form-group"}),
    )
    # Filtros adicionales
    filter_type = forms.ChoiceField(
        choices=[
            ("all", "Todos"),
            ("free", "Free"),
            ("suscription", "Suscripción"),
            ("pay", "Pago"),
        ],
        required=False,
        label="Filtrar por tipo",
        widget=forms.Select,
    )


class ArticleFilterForm(forms.Form):
    """
    Formulario para filtrar artículos por tags, categoría y tipo de categoría.
    """

    # Filtro de tags
    tags = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="Filtrar por tag",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    # Filtro de categorías
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Filtrar por categoría",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    # Filtro de tipo de categoría
    category_type = forms.ChoiceField(
        choices=[
            ("all", "Todos"),
            ("free", "Gratis"),
            ("suscription", "Suscripción"),
            ("pay", "Pago"),
        ],
        required=False,
        label="Filtrar por tipo de categoría",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

