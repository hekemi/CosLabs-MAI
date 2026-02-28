from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Client(models.Model):
    name = models.CharField(max_length=255, unique=True)
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                          validators=[MinValueValidator(0)])
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comment = models.TextField(blank=True)

    @property
    def credit_remaining(self):
        return self.credit_limit - self.current_debt

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    PAYMENT_CHOICES = [
        ("cash", "Наличный расчет"),
        ("noncash", "Безналичный расчет"),
        ("credit", "Кредит"),
        ("barter", "Бартер"),
        ("offset", "Взаимозачет"),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Заказ #{self.id} ({self.client.name})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
