from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from app.models import Employee


class EmployeeAddForm(forms.Form):

    username = forms.CharField(max_length="100")
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)




class EmployeeChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField(
        help_text="<a href=\"password/\">Hier können sie ihr Passwort ändern</a>")

    class Meta:
        model = Employee
        exclude = []
