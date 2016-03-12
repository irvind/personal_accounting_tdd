from django.test import LiveServerTestCase, override_settings

from selenium import webdriver


class HomePageTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def check_find_exp_item(self, name, price):
        elements = self.browser.find_elements_by_css_selector(
            '#main_item_box > .item'
        )

        for elem in elements:
            self.assertEqual(
                elem.find_element_by_css_selector('span.item-name').text,
                name
            )

            self.assertEqual(
                float(elem.find_element_by_css_selector('span.item-price').text),
                price
            )

    @override_settings(DEBUG=True)
    def test_home_page(self):
        self.browser.get(self.live_server_url)
        self.assertIn('Учет расходов', self.browser.title)

        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Расходы / Доходы', header.text)

        # Находим сколько мы потратили на данный момент
        spent = float(self.browser.find_element_by_id('spent_amount').text)

        # Записываем что сегодня потратили
        new_item_text_elem = self.browser.find_element_by_id('new_item_text')
        self.assertEqual(
            new_item_text_elem.get_attribute('placeholder'),
            'Наименование траты'
        )

        new_item_text_elem.send_keys('Ненужная штуковина')

        new_item_price_elem = self.browser.find_element_by_id('new_item_price')
        self.assertEqual(
            new_item_price_elem.get_attribute('placeholder'),
            'Сколько'
        )

        new_item_price_elem.send_keys('100.50')
        expected_spent = spent - 100.50

        # Жмем записать
        self.browser.find_element_by_id('add_new_item').click()

        # Должны увидеть наш пункт в списке
        self.check_find_exp_item('Ненужная штуковина', 100.50)

        # Должны увидеть что расходы увеличились
        self.assertEqual(
            float(self.browser.find_element_by_id('spent_amount').text),
            expected_spent
        )

        # Заходим на сайт позже и расчитываем увидеть наши заполненные данные
        self.browser.get(self.live_server_url)

        self.check_find_exp_item('Ненужная штуковина', 100.50)