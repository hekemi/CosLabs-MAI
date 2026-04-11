from django.core.exceptions import ValidationError
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f'{self.code} — {self.name}'


class Asset(models.Model):
    name = models.CharField(max_length=150)
    storage_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='assets',
        verbose_name='Место хранения (подразделение)',
    )
    internal_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Код внутреннего учета',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def assign_internal_code(self):
        dept = self.storage_department
        seq = (
            Asset.objects
            .filter(storage_department=dept)
            .exclude(pk=self.pk)
            .count() + 1
        )
        self.internal_code = f'{dept.code}{seq:04d}'

    def __str__(self):
        return f'{self.name} ({self.internal_code or "без кода"})'


class Counterparty(models.Model):
    name = models.CharField(max_length=150, verbose_name='Наименование')
    code = models.CharField(max_length=30, verbose_name='Код', blank=True)
    inn = models.CharField(max_length=20, verbose_name='ИНН')
    marked_for_deletion = models.BooleanField(default=False, verbose_name='Помечен на удаление')

    class Meta:
        unique_together = ('code', 'inn')

    def save(self, *args, **kwargs):
        # Автоматически генерируем код если его нет
        if not self.code:
            last = Counterparty.objects.order_by('-id').first()
            next_num = (last.id if last else 0) + 1
            self.code = f'CP_{next_num:04d}'
        
        self.inn = (self.inn or '').strip()
        if not self.inn:
            raise ValidationError({'inn': 'ИНН не может быть пустым.'})
        
        super().save(*args, **kwargs)

    def clean(self):
        self.inn = (self.inn or '').strip()
        if not self.inn:
            raise ValidationError({'inn': 'ИНН не может быть пустым.'})

    def __str__(self):
        return f'{self.name} [{self.code}]'