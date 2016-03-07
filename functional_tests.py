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

        # Находим сколько мы потратили на данный момент
        self.fail('Finish me')

        # Записываем что сегодня потратили

        # Жмем записать

        # Должны увидеть наш пункт в списке
        # Должны увидеть что расходы увеличились

        # Повторяем

        # Заходим на сайт позже и расчитываем увидеть наши заполненные данные

if __name__ == '__main__':
    unittest.main()
