from django.db import models


class Employee(models.Model):
    last_name = models.CharField("Фамилия", max_length=100)
    first_name = models.CharField("Имя", max_length=100)
    patronymic = models.CharField("Отчество", max_length=100, blank=True)
    position = models.CharField("Должность", max_length=150)
    address = models.CharField("Адрес", max_length=255)
    personal_phone = models.CharField("Личный телефон", max_length=30)
    work_phone = models.CharField("Рабочий телефон", max_length=30)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ("last_name", "first_name", "patronymic")

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()
