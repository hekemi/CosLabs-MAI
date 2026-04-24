from django.db import models


class Product(models.Model):
    name = models.CharField('Название товара', max_length=255)

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField('Склад', max_length=255)

    def __str__(self):
        return self.name


class StockEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name='Склад')
    quantity = models.PositiveIntegerField('Количество')
    unit_price = models.DecimalField('Цена за единицу', max_digits=12, decimal_places=2)
    delivery_date = models.DateField('Дата завоза')

    class Meta:
        verbose_name = 'Поступление товара'
        verbose_name_plural = 'Поступления товаров'

    def __str__(self):
        return f'{self.product} / {self.warehouse}'