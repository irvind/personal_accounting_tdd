from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Sum


from .models import Expense


def index_view(request):
    _sum = Expense.objects.aggregate(
        sum=Sum('price')
    )['sum']

    _sum = -_sum if _sum is not None else 0

    return render(request, 'accounting/index.html', {
        'exp_sum': _sum,
        'exp_items': Expense.objects.order_by('-id')
    })


def new_expense_view(request):
    name = request.POST.get('name')
    price = request.POST.get('price')

    try:
        price = float(price)
    except (TypeError, ValueError):
        pass

    if name and isinstance(price, float):
        exp = Expense.objects.create(
            name=request.POST['name'],
            price=price
        )

    return redirect(reverse('accounting:index'))
