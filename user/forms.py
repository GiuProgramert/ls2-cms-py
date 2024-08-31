from django import forms
from .models import CustomUser, Role

class RoleAssignmentForm(forms.ModelForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['roles']
