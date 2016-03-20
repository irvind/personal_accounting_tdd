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
