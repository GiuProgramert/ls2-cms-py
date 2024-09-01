from django import forms
from .models import CustomUser, Role
from django.contrib.auth.forms import UserCreationForm


class RoleAssignmentForm(forms.ModelForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(), widget=forms.CheckboxSelectMultiple, required=True
    )

    class Meta:
        model = CustomUser
        fields = ["roles"]

#form que el usuario debe completar para poder registrarse
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
