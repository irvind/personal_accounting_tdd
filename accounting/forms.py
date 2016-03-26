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
        create_kwargs = {
            'name': expense['name'],
            'price': expense['price'],
        }

        if 'date' in expense:
            create_kwargs['date'] = expense['date']
        if 'quantity' in expense:
            quant = expense['quantity']
            if quant[0] == 'countable':
                create_kwargs.update({
                    'unit': 'x',
                    'amount': quant[1]
                })
            elif quant[0] == 'measurable':
                create_kwargs.update({
                    'unit': quant[1],
                    'amount': quant[2]
                })

        return Expense.objects.create_expense(**create_kwargs)
