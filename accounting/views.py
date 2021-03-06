from django.shortcuts import render, redirect

from .models import Expense
from .forms import ExpenseForm


def index_view(request):
    form = ExpenseForm()

    if request.method == 'POST':
        form = ExpenseForm(data=request.POST)
        if form.is_valid():
            form.save()

        return redirect('accounting:index')

    return render(request, 'accounting/index.html', {
        'form': form,
        'exp_sum': Expense.get_total_expense(),
        'exp_items': Expense.objects.order_by('-id'),
    })
