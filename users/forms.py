from django import forms
from .models import CustomUser


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email", "password"]
        widgets = {"password": forms.PasswordInput()}
