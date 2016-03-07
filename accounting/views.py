# from django.shortcuts import render
from django.http import HttpResponse


def index_view(request):
    return HttpResponse(
        '<html><title>Учет расходов</title><body>'
        '<h1>Расходы / Доходы</h1><div id="main-item-box"></div>'
        '</body></html>'
    )
