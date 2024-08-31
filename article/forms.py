from django import forms
from article.models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'type', 'state', 'is_moderated']

        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
            'type': 'Tipo',
            'state': 'Estado',
            'is_moderated': 'Moderado',
        }
