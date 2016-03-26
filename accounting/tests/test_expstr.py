from unittest import skip

from datetime import date

from .base import BaseTestCase

from accounting.expstr import (
    get_expstr_token_type, parse_expstr, EXPSTR_NO_NAME, EXPSTR_INVALID_NAME,
    EXPSTR_NO_PRICE
)
from accounting.exceptions import ExpstrError


class ParseExpstrTest(BaseTestCase):
    def test_simple_case(self):
        ret = parse_expstr('Предмет 12.10')
        self.assertEqual(ret['name'], 'Предмет')
        self.assertEqual(ret['price'], 12.1)

    def test_complex_name(self):
        ret = parse_expstr('Какой-то предмет 12.10руб.')
        self.assertEqual(ret['name'], 'Какой-то предмет')
        self.assertEqual(ret['price'], 12.1)

    def test_price_and_date(self):
        ret = parse_expstr('Предмет 12.10 12.01.2015')
        self.assertEqual(ret['price'], 12.1)
        self.assertEqual(ret['date'], date(2015, 1, 12))

    def test_implicit_date(self):
        year = date.today().year
        ret = parse_expstr('Предмет 12.10р 12.01')
        self.assertEqual(ret['date'], date(year, 1, 12))

    def test_parses_full_date_with_following_zero(self):
        ret = parse_expstr('Предмет 12.10р 02.01.2005')
        self.assertEqual(ret['date'], date(2005, 1, 2))

        year = date.today().year
        ret = parse_expstr('Предмет 12.10р 02.01')
        self.assertEqual(ret['date'], date(year, 1, 2))

    def test_parses_explicit_date_without_year(self):
        year = date.today().year
        ret = parse_expstr('Булка 25.10 25.10д')
        self.assertEqual(ret['date'], date(year, 10, 25))

    def test_countable_quantity(self):
        ret = parse_expstr('Предмет 12.10 x4')
        self.assertEqual(ret['quantity'], ('countable', 4))
        ret = parse_expstr('Предмет 12.10 4x')
        self.assertEqual(ret['quantity'], ('countable', 4))
        ret = parse_expstr('Предмет 12.10 х10')   # rus x
        self.assertEqual(ret['quantity'], ('countable', 10))
        ret = parse_expstr('Предмет 12.10 10х')   # rus x
        self.assertEqual(ret['quantity'], ('countable', 10))

    def test_mesurable_quantity(self):
        ret = parse_expstr('Предмет 12.10 3.4кг')
        self.assertEqual(ret['quantity'], ('measurable', 'kg', 3.4))
        ret = parse_expstr('Предмет 12.10 345г')
        self.assertEqual(ret['quantity'], ('measurable', 'g', 345))
        ret = parse_expstr('Предмет 12.10 900мл')
        self.assertEqual(ret['quantity'], ('measurable', 'ml', 900))
        ret = parse_expstr('Предмет 12.10 9.5л')
        self.assertEqual(ret['quantity'], ('measurable', 'l', 9.5))

    def test_returns_only_passed_data(self):
        ret = parse_expstr('Предмет 12.10р')
        self.assertIsNone(ret.get('quantity'))
        self.assertIsNone(ret.get('date'))
        self.assertIsNotNone(ret.get('name'))
        self.assertIsNotNone(ret.get('price'))

    def test_price_not_set_error(self):
        with self.assertRaises(ExpstrError) as cm:
            parse_expstr('Предмет 3.4кг 10.10.2015')

        self.assertEqual(
            cm.exception.error_desc['price'],
            EXPSTR_NO_PRICE
        )

    def test_name_not_set_error(self):
        with self.assertRaises(ExpstrError) as cm:
            parse_expstr('3.4кг')

        self.assertEqual(
            cm.exception.error_desc['name'],
            EXPSTR_NO_NAME
        )

    def test_invalid_name(self):
        with self.assertRaises(ExpstrError) as cm:
            parse_expstr('Предмет 12.40 3.4кг какой-то')
        self.assertEqual(
            cm.exception.error_desc['name'],
            EXPSTR_INVALID_NAME
        )

        with self.assertRaises(ExpstrError) as cm:
            parse_expstr('12.40 3.4кг Предмет какой-то')
        self.assertEqual(
            cm.exception.error_desc['name'],
            EXPSTR_INVALID_NAME
        )

    def test_ambiguity_between_date_and_price(self):
        with self.assertRaises(ExpstrError) as cm:
            parse_expstr('Предмет 12.12 12.12')

        self.assertEqual(
            cm.exception.error_desc['price'],
            'Cannot determine price'
        )

    # todo: remove skip and fix
    @skip
    def test_duplicated_tokens_raises_error(self):
        with self.assertRaises(ExpstrError) as cm:
            parse_expstr('Предмет 12.12р 12.12р')

        self.assertEqual(
            cm.exception.error_desc['price'],
            'Duplicated price'
        )

        with self.assertRaises(ExpstrError) as cm:
            parse_expstr('Предмет 12.12р 12.12д 12.12.2005')

        self.assertEqual(
            cm.exception.error_desc['date'],
            'Duplicated date'
        )

        with self.assertRaises(ExpstrError) as cm:
            parse_expstr('Предмет 12.12р 1x 34кг')

        self.assertEqual(
            cm.exception.error_desc['quantity'],
            'Duplicated quantity'
        )

    def test_extra_dateprice_token_error(self):
        with self.assertRaises(ExpstrError) as cm:
            parse_expstr('Предмет 12.12р 12.12д 12.10')

        self.assertEqual(
            cm.exception.error_desc['price'],
            'Duplicated price'
        )


class GetExpTokenTest(BaseTestCase):
    def test_raises_exception_on_blank_token(self):
        with self.assertRaises(ValueError):
            get_expstr_token_type('')
        with self.assertRaises(ValueError):
            get_expstr_token_type('  \t\t\n\n ')

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

    def test_can_recognize_implicit_date_token(self):
        self.assertEqual(get_expstr_token_type('23.12.2015'), ('date',))
        self.assertEqual(get_expstr_token_type('10.05.2014'), ('date',))
        self.assertEqual(get_expstr_token_type('01.05.2014'), ('date',))

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
        self.assertEqual(get_expstr_token_type('34кг.'), ('quantity',))
        self.assertEqual(get_expstr_token_type('340.5г'), ('quantity',))
        self.assertEqual(get_expstr_token_type('340.5г.'), ('quantity',))
        self.assertEqual(get_expstr_token_type('340.50мл'), ('quantity',))
        self.assertEqual(get_expstr_token_type('2.5л'), ('quantity',))

    # todo: errors on explicit
