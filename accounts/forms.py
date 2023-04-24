from django import forms
from django.contrib.auth.models import User
from .models import Profile

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',widget=forms.PasswordInput)
    password_2 = forms.CharField(label='try password',widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username','first_name','email']

    def clean_password2(self):
        data = self.cleaned_data
        if data['password'] != data['password2']:
            raise forms.ValidationError['Paroliniz bir birge teng boliw kerek']
        return data['password2'] 
    
class UserEdirForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email']

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth','photo']