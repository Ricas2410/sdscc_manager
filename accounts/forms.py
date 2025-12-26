from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, UserProfile

class SDSCCUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('member_id', 'first_name', 'last_name', 'email', 'phone', 'role', 'branch')

class SDSCCUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('member_id', 'first_name', 'last_name', 'email', 'phone', 'role', 'branch', 'is_active')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'baptism_date': forms.DateInput(attrs={'type': 'date'}),
            'membership_date': forms.DateInput(attrs={'type': 'date'}),
        }
