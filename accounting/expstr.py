import re

from datetime import date


explicit_price_token_regex = r'^(\d+(?:\.\d{1,2})?)(?:р|руб\.?)$'
explicit_date_token_regex = r'^(\d|1\d|2\d|3[01]).([01]\d)(?:.(\d{4}))?д$'
implicit_full_date_token_regex = r'(\d|1\d|2\d|3[01]).([01]\d).(\d{4})$'
quantity_token_regex = r'([xXхХ]\d+|\d+[xXхХ]|\d+(?:\.\d+)?(кг|г|л|мл)\.?)'
number_2dec_token_regex = r'^\d+(\.\d{1,2})?$'
name_token_regex = r'^.+$'


def parse_expstr(exp_string):
    tokens = exp_string.split(' ')

    tokens_with_type = []
    for token in tokens:
        # types = get_expstr_token_type(token)
        # tokens_with_type = [(token, get_expstr_token_type()) for token in tokens]
        pass


def get_expstr_token_type(token, not_type=None):

    def apply_not_type(result):
        return tuple(r for r in result if r not in not_type)

    if not token.strip():
        raise ValueError('Invalid token')

    not_type = not_type or []

    if re.search(explicit_price_token_regex, token):
        return ('price',)

    if re.search(explicit_date_token_regex, token):
        return ('date',)
    if re.search(implicit_full_date_token_regex, token):
        return ('date',)
    if re.search(quantity_token_regex, token):
        return ('quantity',)

    match = re.search(number_2dec_token_regex, token)
    if match:
        fractional_part = match.group(1)
        if fractional_part is None or len(fractional_part) < 3:
            return ('price',)

        without_point = fractional_part[1:]
        if int(without_point) == 0 or int(without_point) > 12:
            return ('price',)

        today_year = date.today().year
        sp = token.split('.')
        day, month = int(sp[0]), int(sp[1])
        try:
            _ = date(today_year, month, day)
        except ValueError:
            return ('price',)

        return apply_not_type(('price', 'date'))

    elif re.search(name_token_regex, token):
        return ('name',)

    return None
