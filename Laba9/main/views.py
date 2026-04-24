import os

from django.db.models.aggregates import Sum
from django.db.models import FloatField, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect
from django.views.generic import ListView

from lab9 import settings
from .forms import AddCar, AddDriver, AddTrip
from .models import Car, Driver, Trip

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def index(request):
    car_all = Car.objects.all()
    miles = []
    marks = []
    sum_mil = 0.0

    for car in car_all:
        m = float(car.mileage or 0)
        sum_mil += m
        miles.append(m)
        marks.append(car.marks)

    avg_mil = (sum_mil / len(marks)) if marks else 0.0

    plt.clf()
    plt.bar(marks, miles, label='Пробег')
    plt.axhline(y=avg_mil, label=f"Среднее значение = {avg_mil}", color='red')
    plt.title('Пробег авто по маркам')
    plt.xlabel('Марка')
    plt.ylabel('Пробег, км')
    plt.legend()

    path = os.path.join(settings.BASE_DIR, "main", "static", "main", "gh", "graph_mil.png")
    plt.savefig(path)

    c = Driver.objects.annotate(
        total_distance=Coalesce(Sum('trips__distance'), Value(0.0), output_field=FloatField())
    )

    name = []
    miles = []
    sum_mil = 0.0

    for driver in c:
        d = float(driver.total_distance or 0)
        sum_mil += d
        miles.append(d)
        name.append(driver.name)

    avg_mil = (sum_mil / len(name)) if name else 0.0

    plt.clf()
    plt.bar(name, miles, label='Общий пробег')
    plt.axhline(y=avg_mil, label=f"Среднее значение = {avg_mil}", color='red')
    plt.title('Общий пробег')
    plt.xlabel('Имя')
    plt.ylabel('Пробег, км')
    plt.legend()

    path = os.path.join(settings.BASE_DIR, "main", "static", "main", "gh", "graph_name.png")
    plt.savefig(path)

    return render(request, 'main/index.html')


class CarListView(ListView):
    model = Car
    template_name = 'main/car.html'
    context_object_name = 'cars'

    def get_context_data(self, *, object_list =None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AddCar()
        return context

    def post(self, request, *args, **kwargs):
        form=AddCar(request.POST)
        if form.is_valid():
            form.save()
        return redirect('car')


class DriverListView(ListView):
    model = Driver
    template_name = 'main/driver.html'
    context_object_name = 'drivers'

    def get_queryset(self):
        return Driver.objects.annotate(
            total_distance=Coalesce(Sum('trips__distance'), Value(0.0), output_field=FloatField())
        )


    def get_context_data(self, *, object_list =None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AddDriver()
        return context

    def post(self, request, *args, **kwargs):
        form=AddDriver(request.POST)
        if form.is_valid():
            form.save()
        return redirect('driver')


class TripListView(ListView):
    model = Trip
    template_name = 'main/trip.html'
    context_object_name = 'trips'

    def get_context_data(self, *, object_list =None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AddTrip()
        return context

    def post(self, request, *args, **kwargs):
        form = AddTrip(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            start = form.cleaned_data['start_km']
            end = form.cleaned_data['end_km']
            trip.distance = end - start
            trip.fuel = trip.distance * trip.car.fuel_consumption
            trip.car.mileage += trip.distance
            trip.car.save()
            trip.save()
            return redirect('trip')
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)

