from django.test import TestCase
from django.test.client import Client

from django.core.urlresolvers import reverse


class BaseTestCase(TestCase):
    def setUp(self):
        self.c = Client()


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
