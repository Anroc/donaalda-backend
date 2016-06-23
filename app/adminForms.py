from django import forms
from django.contrib.auth.forms import (UserCreationForm,
                                       UserChangeForm)
from django.contrib.auth import password_validation
from .models import Employee


class EmployeeCreationForm(forms.ModelForm):

    error_messages = {
        'password_mismatch': "Die beiden Passwörter stimmen nicht überein",
    }
    password1 = forms.CharField(label="Passwort",
                                strip=False,
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label="Passwort bestätigen",
                                widget=forms.PasswordInput,
                                strip=False,
                                help_text="Tragen Sie zur Bestätigung hier bitte dasselbe Passwort noch einmal ein.")

    class Meta:
        model = Employee
        fields = ("username", "employer",)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def save(self, commit=True):
        employee = super(EmployeeCreationForm, self).save(commit=False)
        employee.set_password(self.cleaned_data["password1"])
        if commit:
            employee.save()
        return employee


class EmployeeChangeForm(UserChangeForm):
    class Meta:
        model = Employee
        exclude = []
