import datetime

from decimal import Decimal

from django.db import models
from django.db.models import Sum


def invert_dict(di):
    return {
        v: k for k, v in di.items()
    }


class ExpenseManager(models.Manager):
    @staticmethod
    def create_expense(name, price=None, unit='x', amount=1,
                       unit_price=None, **kwargs):
        if price is None and unit_price is not None:
            price = unit_price * amount

        price = round(Decimal(price), 2)

        key = 'countable_amount' if unit == 'x' else 'mesurable_amount'
        kwargs[key] = amount

        exp = Expense(
            name=name,
            price=price,
            unit_type=unit,
            unit_price=unit_price,
            **kwargs
        )
        exp.full_clean()
        exp.save()
        return exp


class Expense(models.Model):
    UNIT_TYPE_CHOICES = (
        ('x', 'Неделимые'),
        ('kg', 'Килограммы'),
        ('g', 'Граммы'),
        ('l', 'Литры'),
        ('ml', 'Миллилитры'),
    )

    rus_type_choice_mapping = {
        'kg': 'кг',
        'g': 'г',
        'l': 'л',
        'ml': 'мл',
    }

    objects = ExpenseManager()

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField(default=datetime.date.today)
    unit_type = models.CharField(
        max_length=2,
        choices=UNIT_TYPE_CHOICES,
        default='x'
    )
    countable_amount = models.IntegerField(null=True, blank=True)
    mesurable_amount = models.FloatField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    created = models.DateField(auto_now_add=True)

    @classmethod
    def get_total_expense(cls):
        _sum = cls.objects.aggregate(
            sum=Sum('price')
        )['sum']

        return -_sum if _sum is not None else Decimal(0)

    @property
    def amount(self):
        if self.unit_type == 'x':
            return self.countable_amount

        return self.mesurable_amount

    @property
    def quantity_repr(self):
        # todo: move to template filter
        if self.unit_type == 'x':
            return 'x{}'.format(self.countable_amount)
        else:
            amount = self.mesurable_amount
            if amount == int(amount):
                amount = int(amount)

            return '{} {}'.format(
                amount,
                self.rus_type_choice_mapping[self.unit_type]
            )

    @classmethod
    def eng_unit_type_to_rus(cls, eng_unit):
        return cls.rus_type_choice_mapping[eng_unit]

    @classmethod
    def rus_unit_type_to_eng(cls, rus_unit):
        di = invert_dict(cls.rus_type_choice_mapping)
        return di[rus_unit]
