from decimal import Decimal
from django.db import models


class ProductStock(models.Model):
    product_name = models.CharField("Название товара", max_length=255)
    quantity = models.PositiveIntegerField("Количество")
    unit_price = models.DecimalField("Цена за штуку", max_digits=12, decimal_places=2)
    total_cost = models.DecimalField("Стоимость", max_digits=14, decimal_places=2, editable=False)
    arrival_date = models.DateField("Дата завоза")

    class Meta:
        verbose_name = "Остаток товара"
        verbose_name_plural = "Остатки товаров"
        ordering = ["-arrival_date", "product_name"]

    def save(self, *args, **kwargs):
        qty = Decimal(str(self.quantity or 0))
        price = Decimal(str(self.unit_price or 0))
        self.total_cost = (qty * price).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} ({self.arrival_date})"
