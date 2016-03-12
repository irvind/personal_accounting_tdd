from unittest import skip

from django.test import TestCase
from django.test.client import Client

from django.core.urlresolvers import reverse

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

    @skip
    def test_cannot_create_if_name_is_missing(self):
        resp = self.c.post(
            reverse('accounting:new_expense'),
            {'name': 'some name'}
        )

        self.assertEqual(resp.status_code, 400)


class IndexNewExpenseIntegrationTest(BaseTestCase):
    @skip
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
