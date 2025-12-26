from django import forms
from .models import Member, MemberDocument, DeceasedMember

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        exclude = ('user',)
        widgets = {
            'transfer_date': forms.DateInput(attrs={'type': 'date'}),
            'baptism_date': forms.DateInput(attrs={'type': 'date'}),
            'position_start_date': forms.DateInput(attrs={'type': 'date'}),
        }

class MemberDocumentForm(forms.ModelForm):
    class Meta:
        model = MemberDocument
        fields = ('document_type', 'title', 'file', 'description')

class DeceasedMemberForm(forms.ModelForm):
    class Meta:
        model = DeceasedMember
        exclude = ('contribution_collected', 'is_contribution_closed')
        widgets = {
            'date_of_death': forms.DateInput(attrs={'type': 'date'}),
            'date_of_burial': forms.DateInput(attrs={'type': 'date'}),
        }
