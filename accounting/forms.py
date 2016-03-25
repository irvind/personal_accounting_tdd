from django import forms
from django.core.exceptions import ValidationError

from .models import Expense
from .utils import remove_extra_spaces
from .expstr import parse_expstr
from .exceptions import ExpstrError


class ExpenseForm(forms.Form):
    expense = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Наименование траты, сколько, стоимость, когда'
        })
    )

    def clean_expense(self):
        expense = self.cleaned_data['expense']

        try:
            ret = parse_expstr(remove_extra_spaces(expense))
        except ExpstrError as e:
            raise ValidationError('Ошибка в описании траты')

        return ret

    def save(self):
        if not self.is_valid():
            raise ValueError('Form is not valid')

        expense = self.cleaned_data['expense']

        return Expense.objects.create(
            name=expense['name'],
            price=expense['price'],
        )
