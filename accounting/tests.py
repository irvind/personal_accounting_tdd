from django.test import TestCase
from django.test.client import Client

from django.core.urlresolvers import reverse


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

    def test_index_page_accepts_new_items(self):
        item_name, item_price = 'Бананы', 70

        response = self.c.post(
            reverse('accounting:index'),
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
