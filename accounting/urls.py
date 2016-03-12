from django.conf.urls import url


from . import views


urlpatterns = [
    url(r'^$', views.index_view, name='index'),
    url(r'^new-expense$', views.new_expense_view, name='new_expense')
]
