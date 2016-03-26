from unittest import skip

from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.core.exceptions import ValidationError

from accounting.models import Expense


class ExpenseModelTest(TestCase):
    def test_can_create_model(self):
        Expense.objects.create_expense(
            name='Some item',
            price=123.45
        )

        exp = Expense.objects.last()
        self.assertEqual(exp.name, 'Some item')
        self.assertEqual(exp.price, Decimal('123.45'))
        self.assertEqual(exp.date, date.today())

    def test_can_create_countable(self):
        Expense.objects.create_expense(
            name='Some item',
            unit='x',
            amount=3,
            unit_price=60
        )

        exp = Expense.objects.last()
        self.assertEqual(exp.name, 'Some item')
        self.assertEqual(exp.unit_type, 'x')
        self.assertEqual(exp.amount, 3)
        self.assertEqual(exp.unit_price, 60)
        self.assertEqual(exp.price, 180)

    def test_creates_one_countable_by_default(self):
        Expense.objects.create_expense(
            name='Some item',
            price=60
        )

        exp = Expense.objects.last()
        self.assertEqual(exp.unit_type, 'x')
        self.assertEqual(exp.amount, 1)

    def test_can_create_measurable(self):
        Expense.objects.create_expense(
            name='Some item',
            unit='kg',
            amount=2.5,
            unit_price=100
        )

        exp = Expense.objects.last()
        self.assertEqual(exp.unit_type, 'kg')
        self.assertEqual(exp.amount, 2.5)
        self.assertEqual(exp.unit_price, 100)
        self.assertEqual(exp.price, 250)

        Expense.objects.create_expense(
            name='Some item',
            unit='g',
            amount=700,
            unit_price=3
        )
        exp = Expense.objects.last()
        self.assertEqual(exp.unit_type, 'g')

    def test_cannot_create_exp_with_blank_name(self):
        with self.assertRaises(ValidationError):
            Expense.objects.create_expense(
                name='',
                price=200.5
            )

    def test_cannot_create_exp_with_invalid_unit(self):
        with self.assertRaises(ValidationError):
            Expense.objects.create_expense(
                name='some item',
                price=200.5,
                unit='г',
                amount=200
            )

    @skip
    def test_cannot_create_exp_with_negative_or_zero_price(self):
        with self.assertRaises(ValidationError):
            Expense.objects.create_expense(
                name='some item',
                price=0
            )

        with self.assertRaises(ValidationError):
            Expense.objects.create_expense(
                name='some item',
                price=-100
            )

    def test_total_expense_returns_correct_price(self):
        Expense.objects.create(name='Some item', price=60.40)
        Expense.objects.create(name='Some item 2', price=20.30)
        Expense.objects.create(name='Some item 3', price=20.35)

        total_exp = Expense.get_total_expense()

        self.assertIsInstance(total_exp, Decimal)
        self.assertEqual(total_exp, Decimal('-101.05'))

    def test_total_expense_returns_null_if_dont_have_exp_items(self):
        self.assertEqual(Expense.get_total_expense(), Decimal('0'))
