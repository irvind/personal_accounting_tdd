from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from .models import Expense


def index_view(request):
    return render(request, 'accounting/index.html')


def new_expense_view(request):
    exp = Expense.objects.create(
        name=request.POST['name'],
        price=int(request.POST['price'])
    )
    return redirect(reverse('accounting:index'))
