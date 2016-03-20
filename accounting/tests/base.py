from django.test import TestCase
from django.test.client import Client

from bs4 import BeautifulSoup


class BaseTestCase(TestCase):
    def setUp(self):
        self.c = Client()

    def assertContainsHtml(self, resp, html):
        self.assertContains(
            resp,
            html,
            html=True
        )

    def get_page_soup(self, response):
        return BeautifulSoup(response.content, 'lxml')
