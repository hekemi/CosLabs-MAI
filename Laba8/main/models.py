from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField()
    price = models.FloatField()

