from selenium import webdriver
import unittest


class HomePageTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_home_page(self):
        self.browser.get('http://localhost:8000')
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
        first_item = self.browser.find_elements_by_css_selector(
            '#main_item_box > .item'
        )[0]

        self.assertEqual(
            first_item.find_element_by_css_selector('span.item-name').text,
            'Ненужная штуковина'
        )

        self.assertEqual(
            float(first_item.find_element_by_css_selector('span.item-price').text),
            100.50
        )

        # Должны увидеть что расходы увеличились
        self.assertEqual(
            float(self.browser.find_element_by_id('spent_amount').text),
            expected_spent
        )

        # Заходим на сайт позже и расчитываем увидеть наши заполненные данные
        self.fail('Finish me')

if __name__ == '__main__':
    unittest.main()
