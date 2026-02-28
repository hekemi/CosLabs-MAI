from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock_qty']
        labels = {
            'name': 'Название товара',
            'price': 'Цена',
            'stock_qty': 'Количество на складе',
        }