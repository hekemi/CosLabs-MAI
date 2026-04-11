from django import forms
from .models import Asset, Counterparty


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'storage_department', 'internal_code']
        widgets = {
            'internal_code': forms.TextInput(attrs={'readonly': 'readonly'}),
        }


class CounterpartyForm(forms.ModelForm):
    class Meta:
        model = Counterparty
        fields = ['name', 'code', 'inn']