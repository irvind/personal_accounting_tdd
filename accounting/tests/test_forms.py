from .base import BaseTestCase

from accounting.forms import ExpenseForm
from accounting.models import Expense


class ExpenseFormTest(BaseTestCase):
    def test_simple_expense_create(self):
        form = ExpenseForm(data={'expense': 'Предмет 10.50'})
        form.save()

        expense = Expense.objects.first()

        self.assertEqual(expense.name, 'Предмет')
        self.assertEqual(expense.price, 10.50)

    def test_save_item_with_price_with_postfix(self):
        form = ExpenseForm(data={'expense': 'Предмет1 20.50р'})
        form.save()

        expense = Expense.objects.last()

        self.assertEqual(expense.name, 'Предмет1')
        self.assertEqual(expense.price, 20.5)

        form = ExpenseForm(data={'expense': 'Предмет2 30.50руб'})
        form.save()

        expense = Expense.objects.last()

        self.assertEqual(expense.name, 'Предмет2')
        self.assertEqual(expense.price, 30.5)
