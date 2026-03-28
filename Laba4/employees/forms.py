from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "last_name",
            "first_name",
            "patronymic",
            "position",
            "address",
            "personal_phone",
            "work_phone",
        ]