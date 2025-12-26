from django import forms
from .models import Contribution, Remittance

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ('member', 'contribution_type', 'amount', 'date', 'reference', 'notes')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

class RemittanceForm(forms.ModelForm):
    class Meta:
        model = Remittance
        fields = ('amount', 'period_start', 'period_end', 'notes', 'proof_of_payment')
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
        }
