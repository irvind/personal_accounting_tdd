from datetime import date as date_cls
from unittest import skip

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from bs4 import BeautifulSoup

from accounting.models import Expense


class BaseTestCase(TestCase):
    def setUp(self):
        self.c = Client()

    def assertContainsHtml(self, resp, html):
        self.assertContains(
            resp,
            html,
            html=True
        )

    def get_page_soup(self, page_html):
        return BeautifulSoup(page_html, 'lxml')


class IndexPageViewTest(BaseTestCase):
    def test_index_page_returns_correct_html(self):
        response = self.c.get(reverse('accounting:index'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            '<h1>Расходы / Доходы</h1>',
            html=True
        )

        self.assertContains(
            response,
            '<title>Учет расходов</title>',
            html=True
        )

        self.assertContains(
            response,
            '<div id="main_item_box">',
            html=True
        )

    def test_correct_exp_sum(self):

        def get_spent_amount():
            response = self.c.get(reverse('accounting:index'))
            soup = self.get_page_soup(response.content)
            spent = float(soup.select('#spent_amount')[0].text)
            return spent

        self.assertEqual(get_spent_amount(), 0)

        Expense.objects.create(name='none', price=100.50)
        self.assertEqual(get_spent_amount(), -100.50)

    def test_contain_new_exp_item(self):
        exp = Expense.objects.create(name='my item', price=100.50)

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


class NewExpenseViewTest(BaseTestCase):
    def test_creates_new_expense_model(self):
        item_name, item_price = 'Бананы', 70

        resp = self.c.post(
            reverse('accounting:new_expense'),
            {'name': item_name, 'price': item_price}
        )

        self.assertRedirects(resp, reverse('accounting:index'))

        self.assertEqual(Expense.objects.count(), 1)
        expense = Expense.objects.first()

        self.assertEqual(expense.name, item_name)
        self.assertEqual(expense.price, item_price)

    def test_new_date_is_today(self):
        self.c.post(
            reverse('accounting:new_expense'),
            {'name': 'test', 'price': 5}
        )

        exp = Expense.objects.first()
        self.assertEqual(
            exp.created,
            date_cls.today()
        )

    def test_cannot_create_if_param_is_missing(self):
        resp = self.c.post(
            reverse('accounting:new_expense'),
            {'name': 'some name'}
        )

        self.assertEqual(resp.status_code, 400)

        resp = self.c.post(
            reverse('accounting:new_expense'),
            {'price': '100.05'}
        )

        self.assertEqual(resp.status_code, 400)


class IndexNewExpenseIntegrationTest(BaseTestCase):
    def test_index_page_accepts_new_items(self):
        item_name, item_price = 'Бананы', 70

        response = self.c.post(
            reverse('accounting:new_expense'),
            {'name': item_name, 'price': str(item_price)}
        )

        self.assertRedirects(response, reverse('accounting:index'))

        response = self.c.get(reverse('accounting:index'))

        self.assertContainsHtml(
            response,
            '<span class="item-name">%s</span>' % item_name
        )

        self.assertContainsHtml(
            response,
            '<span class="item-price">%s</span>' % (str(item_price) + '.00')
        )
