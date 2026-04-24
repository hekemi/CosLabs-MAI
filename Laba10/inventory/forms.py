from django import forms
from .models import ProductStock


class ProductStockForm(forms.ModelForm):
    class Meta:
        model = ProductStock
        fields = ["product_name", "quantity", "unit_price", "arrival_date"]
        widgets = {
            "arrival_date": forms.DateInput(attrs={"type": "date"}),
        }