import re

from django import forms

from .models import Expense
from .utils import remove_extra_spaces


class ExpenseForm(forms.Form):
    expense = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Наименование траты, сколько, стоимость, когда'
        })
    )

    def clean_expense(self):
        expense = self.cleaned_data['expense']

        # todo

        return expense

    def save(self):
        if not self.is_valid():
            raise ValueError('Form is not valid')

        expense = remove_extra_spaces(self.cleaned_data['expense'])
        tokens = expense.split(' ')

        item_name_tokens = []
        item_price = None
        for token in tokens:
            check, price = self._is_price_token(token)
            if check:
                item_price = price
            else:
                item_name_tokens.append(token)

        item_name = ' '.join(item_name_tokens)

        return Expense.objects.create(
            name=item_name,
            price=item_price,
        )

    def _is_price_token(self, token):
        print(token)
        match = re.search(r'^\d+(\.\d{1,2})?$', token)
        if not match:
            return False, None

        return True, float(match.group(0))
