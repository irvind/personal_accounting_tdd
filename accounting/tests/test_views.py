from datetime import date as date_cls
from unittest import skip

from django.core.urlresolvers import reverse

from .base import BaseTestCase

from accounting.models import Expense


class IndexPageViewTest(BaseTestCase):
    def get_spent_amount(self, response):
        soup = self.get_page_soup(response)
        return float(soup.select('#spent_amount')[0].text)

    def test_index_page_uses_index_template(self):
        response = self.c.get(reverse('accounting:index'))
        self.assertTemplateUsed(response, 'accounting/index.html')

    def test_returns_zero_spent_amount_on_fresh_db(self):
        response = self.c.get(reverse('accounting:index'))
        self.assertEqual(self.get_spent_amount(response), 0)

    def test_returns_expense_sum(self):
        # todo: take quantity into account
        Expense.objects.create_expense(name='none', price=100.50)
        Expense.objects.create_expense(name='none 2', price=200.00)

        response = self.c.get(reverse('accounting:index'))

        self.assertEqual(
            self.get_spent_amount(response),
            -(100.50 + 200.00)
        )

    def test_contain_new_exp_item(self):
        # todo: take quantity into account
        exp = Expense.objects.create_expense(
            name='my item',
            price=100.50,
            unit='x',
            amount=5
        )

        response = self.c.get(reverse('accounting:index'))
        self.assertContains(
            response,
            '<span class="item-name">my item</span>',
            html=True
        )

        self.assertContains(
            response,
            '<span class="item-price">100.50</span>',
            html=True
        )

        self.assertContains(
            response,
            '<span class="item-date">%s</span>' % (
                exp.created.strftime('%d.%m.%Y')
            ),
            html=True
        )
        self.assertContains(
            response,
            '<span class="item-quantity">x5</span>',
            html=True
        )

    def test_contains_measurable_items(self):
        Expense.objects.create_expense(
            name='my item 1',
            price=100,
            unit='kg',
            amount=3.4
        )
        Expense.objects.create_expense(
            name='my item 2',
            price=200,
            unit='g',
            amount=350
        )

        response = self.c.get(reverse('accounting:index'))
        self.assertContains(
            response,
            '<span class="item-quantity">350 г</span>',
            html=True
        )
        self.assertContains(
            response,
            '<span class="item-quantity">3.4 кг</span>',
            html=True
        )

    def test_creates_new_expense_model(self):
        self.c.post(
            reverse('accounting:index'),
            {'expense': 'Бананы 70'}
        )

        self.assertEqual(Expense.objects.count(), 1)
        expense = Expense.objects.first()

        self.assertEqual(expense.name, 'Бананы')
        self.assertEqual(expense.price, 70)

    def test_redirects_to_index_page(self):
        resp = self.c.post(
            reverse('accounting:index'),
            {'expense': 'Предмет 70руб'}
        )

        self.assertRedirects(resp, reverse('accounting:index'))

    def test_new_date_is_today(self):
        self.c.post(
            reverse('accounting:index'),
            {'expense': 'Предмет 70руб'}
        )

        exp = Expense.objects.last()
        self.assertEqual(
            exp.created,
            date_cls.today()
        )


# todo: rewrite
class NewExpenseViewTest(BaseTestCase):
    @skip
    def test_cannot_create_if_price_is_missing(self):
        resp = self.c.post(
            reverse('accounting:new_expense'),
            {'name': 'some name'}
        )

        self.assertEqual(resp.status_code, 400)

    @skip
    def test_cannot_create_if_item_name_is_missing(self):
        resp = self.c.post(
            reverse('accounting:new_expense'),
            {'price': '100.05'}
        )

        self.assertEqual(resp.status_code, 400)
