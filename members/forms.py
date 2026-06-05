from django import forms
from django.contrib.auth.models import User
from .models import Member


class MemberForm(forms.ModelForm):

    username = forms.CharField(
        max_length=150
    )

    email = forms.EmailField()

    password = forms.CharField(
        widget=forms.PasswordInput()
    )

    class Meta:

        model = Member

        fields = [
            'firstname',
            'lastname',
            'middlename',
            'phone',
            'joined_date',
            'role',
            'username',
            'email',
            'password'
        ]

        widgets = {
            'joined_date': forms.DateInput(
                attrs={'type': 'date'}
            )
        }