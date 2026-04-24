from django import forms
from django.utils import timezone


class ReportDateForm(forms.Form):
    report_date = forms.DateField(
        label='Дата отчета',
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )