from datetime import datetime, timedelta, date as date_cls

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings

from selenium import webdriver


class AccountingPageTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def check_find_exp_item(self, name, price, date, quantity=None):

        def parse_date(date_str):
            return datetime.strptime(date_str, '%d.%m.%Y').date()

        elements = self.browser.find_elements_by_css_selector(
            '#main_item_box > .item'
        )

        all_table = []
        for elem in elements:
            item_name = elem.find_element_by_css_selector('span.item-name').text
            item_price = float(
                elem.find_element_by_css_selector('span.item-price').text
            )
            item_date = parse_date(
                elem.find_element_by_css_selector('span.item-date').text
            )

            if quantity:
                item_quantity = elem.find_element_by_css_selector(
                    'span.item-quantity'
                ).text
            else:
                item_quantity = None

            all_table.append((item_name, item_price, item_date, item_quantity))

        self.assertIn(
            (name, price, date, quantity),
            all_table
        )

    def type_into_new_expense(self, keys):
        self.browser.find_element_by_id('id_expense').send_keys(keys)

    def current_spent_amount(self):
        return float(self.browser.find_element_by_id('spent_amount').text)

    @override_settings(DEBUG=True)
    def test_home_page(self):
        self.browser.get(self.live_server_url)
        self.assertIn('Учет расходов', self.browser.title)

        header = self.browser.find_element_by_tag_name('h1')
        self.assertEqual('Расходы', header.text)

        today = date_cls.today()

        # Записываем что сегодня потратили
        new_expense_elem = self.browser.find_element_by_id('id_expense')
        self.assertEqual(
            new_expense_elem.get_attribute('placeholder'),
            'Наименование траты, сколько, стоимость, когда'
        )

        self.type_into_new_expense('Ненужная штуковина 100.50')

        expected_spent = self.current_spent_amount() - 100.50

        # Жмем Enter
        self.type_into_new_expense('\n')

        # Должны увидеть наш пункт в списке
        self.check_find_exp_item('Ненужная штуковина', 100.50, today, 'x1')

        # Должны увидеть что расходы увеличились
        self.assertEqual(
            self.current_spent_amount(),
            expected_spent
        )

        # Вводим еще один элемент. 150 руб это за все 3.4кг
        expected_spent = self.current_spent_amount() - 150
        self.type_into_new_expense('Мясо курицы 150р 3.4кг\n')
        self.check_find_exp_item('Мясо курицы', 150, today, '3.4 кг')

        self.assertEqual(
            self.current_spent_amount(),
            expected_spent
        )

        # Вдруг мы вспоминили что вчера потратили еще кое-что. Можем записать
        # дату. Цена с постфиксом а дата - без.
        yesterday = today - timedelta(days=1)
        yesterday_str = '{}.{:02}'.format(yesterday.day, yesterday.month)

        self.type_into_new_expense('Хлеб ржаной 30р {}\n'.format(
            yesterday_str
        ))
        self.check_find_exp_item('Хлеб ржаной', 30, yesterday, 'x1')

        # Вспоминили еще раз но уже на позавчера. Дата с постфиксом,
        # а цена - без.
        double_yesterday = today - timedelta(days=2)
        double_yesterday_str = '{}.{:02}'.format(
            double_yesterday.day,
            double_yesterday.month
        )

        self.type_into_new_expense('Булка 25.10 {}д\n'.format(
            double_yesterday_str
        ))
        self.check_find_exp_item('Булка', 25.1, double_yesterday, 'x1')

        # Заходим на сайт позже и расчитываем увидеть наши заполненные данные
        self.browser.get(self.live_server_url)

        self.check_find_exp_item('Ненужная штуковина', 100.50, today, 'x1')
        self.check_find_exp_item('Мясо курицы', 150, today, '3.4 кг')
        self.check_find_exp_item('Хлеб ржаной', 30, yesterday, 'x1')
        self.check_find_exp_item('Булка', 25.1, double_yesterday, 'x1')

    def test_creating_items_with_with_price_for_unit(self):
        self.browser.get(self.live_server_url)

        today = date_cls.today()

        # Всего 2 кг, цена одного килограмма - 200 руб. Расчитываем получить
        # расход в размере 400 руб.
        self.type_into_new_expense('Мясо свинины 200р/кг 2кг\n')
        self.check_find_exp_item('Мясо свинины', 400, today, '2 кг')

        # Купили 4 булочки с маком по 20 руб каждая. Расчитываем получить
        # расход в размере 80 руб. 'х' - это русский символ.
        self.type_into_new_expense('Булочки с маком 20р/х1 х4\n')
        self.check_find_exp_item('Булочки с маком', 80, today, 'x4')
