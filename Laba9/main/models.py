from django.db import models

class Car(models.Model):
    marks = models.CharField()
    number = models.CharField()
    yers_relize = models.IntegerField()
    fuel_consumption  = models.IntegerField()#расход топлива на км
    mileage = models.FloatField()# пробег

    def __str__(self):
        return self.marks

class Driver(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name


class Trip(models.Model):
    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name='trips'
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    date_out = models.DateField()
    date_in = models.DateField()

    distance = models.FloatField()
    fuel = models.FloatField()
