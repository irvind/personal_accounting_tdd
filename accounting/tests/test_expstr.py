from .base import BaseTestCase

from accounting.expstr import get_expstr_token_type


class GetExpTokenTest(BaseTestCase):
    def test_can_recognize_name_token(self):
        self.assertEqual(
            get_expstr_token_type('Banana'),
            ('name',)
        )

    def test_can_recognize_explicit_price_token(self):
        self.assertEqual(get_expstr_token_type('23руб'), ('price',))
        self.assertEqual(get_expstr_token_type('23р'), ('price',))
        self.assertEqual(get_expstr_token_type('23руб.'), ('price',))

    def test_can_recognize_implicit_price_token(self):
        self.assertEqual(get_expstr_token_type('23'), ('price',))
        self.assertEqual(get_expstr_token_type('23.1'), ('price',))
        self.assertEqual(get_expstr_token_type('23.13'), ('price',))
        self.assertEqual(get_expstr_token_type('23.00'), ('price',))
        self.assertEqual(get_expstr_token_type('31.02'), ('price',))

    def test_can_recognize_explicit_date_token(self):
        self.assertEqual(get_expstr_token_type('23.12д'), ('date',))
        self.assertEqual(get_expstr_token_type('1.06д'), ('date',))

    def test_ambiguity_between_date_and_price_tokens(self):
        self.assertEqual(get_expstr_token_type('23.12'), ('price', 'date',))
        self.assertEqual(get_expstr_token_type('1.02'), ('price', 'date',))

    def test_no_ambiguity_between_date_and_price_if_hint_passed(self):
        self.assertEqual(
            get_expstr_token_type('23.12', not_type=('date',)),
            ('price',)
        )
        self.assertEqual(
            get_expstr_token_type('1.02', not_type=('price',)),
            ('date',)
        )

    def test_can_recognize_countable_quantity(self):
        self.assertEqual(get_expstr_token_type('x1'), ('quantity',))
        self.assertEqual(
            get_expstr_token_type('х2'),    # rus x
            ('quantity',)
        )
        self.assertEqual(get_expstr_token_type('10x'), ('quantity',))
        self.assertEqual(
            get_expstr_token_type('100x'),    # rus x
            ('quantity',)
        )

    def test_can_recognoze_howmuch_quantity(self):
        self.assertEqual(get_expstr_token_type('34кг'), ('quantity',))
        self.assertEqual(get_expstr_token_type('340.5г'), ('quantity',))
        self.assertEqual(get_expstr_token_type('340.50мл'), ('quantity',))
        self.assertEqual(get_expstr_token_type('2.5л'), ('quantity',))
