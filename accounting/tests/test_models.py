from datetime import date
from decimal import Decimal

from django.test import TestCase

from accounting.models import Expense


class ExpenseModelTest(TestCase):
    def test_can_create_model(self):
        Expense.objects.create(
            name='Some item',
            price=123.45
        )

        exp = Expense.objects.last()
        self.assertEqual(exp.name, 'Some item')
        self.assertEqual(exp.price, Decimal('123.45'))
        self.assertEqual(exp.date, date.today())

    def test_total_expense_returns_correct_price(self):
        Expense.objects.create(name='Some item', price=60.40)
        Expense.objects.create(name='Some item 2', price=20.30)
        Expense.objects.create(name='Some item 3', price=20.35)

        total_exp = Expense.get_total_expense()

        self.assertIsInstance(total_exp, Decimal)
        self.assertEqual(total_exp, Decimal('-101.05'))

    def test_total_expense_returns_null_if_dont_have_exp_items(self):
        self.assertEqual(Expense.get_total_expense(), Decimal('0'))
