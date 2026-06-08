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

    def clean_username(self):

        username = self.cleaned_data['username']

        if User.objects.filter(
            username=username
        ).exists():

            raise forms.ValidationError(
                "Username already exists."
            )

        return username
    def clean_email(self):

        email = self.cleaned_data['email']

        if User.objects.filter(
            email=email
        ).exists():

            raise forms.ValidationError(
                "Email already exists."
            )

        return email
        
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