from django import forms
from django.core.exceptions import ValidationError

from .models import *


class AddCar(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['marks','number','yers_relize','fuel_consumption', 'mileage']

        labels = {
            'marks': 'Марка автомобиля',
            'number': 'Номер',
            'yers_relize': 'Год выпуска',
            'fuel_consumption': 'Расход топлива',
            'mileage': 'Пробег',
        }

class AddDriver(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name']
        labels = {'name': 'Имя'}


class AddTrip(forms.ModelForm):
    start_km = forms.FloatField(label='Начальный пробег')
    end_km = forms.FloatField(label='Конечный пробег')

    class Meta:
        model = Trip
        fields = ['driver', 'car', 'date_out', 'date_in']  # поля модели