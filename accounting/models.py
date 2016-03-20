from django.db import models
from django.db.models import Sum


class Expense(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created = models.DateField(auto_now_add=True)

    @classmethod
    def get_total_expense(cls):
        _sum = cls.objects.aggregate(
            sum=Sum('price')
        )['sum']

        return -_sum if _sum is not None else 0
