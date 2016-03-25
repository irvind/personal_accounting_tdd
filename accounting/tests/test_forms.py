from unittest import skip
from datetime import date

from .base import BaseTestCase

from accounting.forms import ExpenseForm
from accounting.models import Expense


class ExpenseFormTest(BaseTestCase):
    def _create_and_save_exp_form(self, exp_str):
        form = ExpenseForm(data={'expense': exp_str})
        form.save()
        return form

    def test_simple_expense_create(self):
        self._create_and_save_exp_form('Предмет 10.50')

        expense = Expense.objects.first()

        self.assertEqual(expense.name, 'Предмет')
        self.assertEqual(expense.price, 10.50)

    def test_empty_expense_is_invalid(self):
        form = ExpenseForm(data={'expense': ''})
        self.assertFalse(form.is_valid())

    def test_dont_allow_to_submit_empty_expense(self):
        form = ExpenseForm(data={'expense': ''})
        with self.assertRaises(ValueError):
            form.save()

    def test_save_item_with_price_with_postfix(self):
        self._create_and_save_exp_form('Предмет1 20.50р')
        expense = Expense.objects.last()
        self.assertEqual(expense.name, 'Предмет1')
        self.assertEqual(expense.price, 20.5)

        self._create_and_save_exp_form('Предмет2 30.50руб')
        expense = Expense.objects.last()
        self.assertEqual(expense.name, 'Предмет2')
        self.assertEqual(expense.price, 30.5)

    def test_save_item_with_date(self):
        year = date.today().year

        self._create_and_save_exp_form('Предмет1 20.50р 1.03')
        expense = Expense.objects.last()
        self.assertEqual(expense.date, date(year, 3, 1))

        self._create_and_save_exp_form('Предмет1 20.50р 1.03.2014')
        expense = Expense.objects.last()
        self.assertEqual(expense.date, date(2014, 3, 1))

    # todo: more test for exp item creation
