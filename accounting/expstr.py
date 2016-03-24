import re

from datetime import date

from .exceptions import ExpstrError


explicit_price_token_regex = r'^(\d+(?:\.\d{1,2})?)(?:р|руб\.?)$'
explicit_date_token_regex = r'^(\d|1\d|2\d|3[01]).([01]\d)(?:.(\d{4}))?д$'
implicit_full_date_token_regex = r'(\d|1\d|2\d|3[01]).([01]\d).(\d{4})$'
quantity_token_regex = r'([xXхХ]\d+|\d+[xXхХ]|\d+(?:\.\d+)?(кг|г|л|мл)\.?)'
number_2dec_token_regex = r'^\d+(\.\d{1,2})?$'
name_token_regex = r'^.+$'

EXPSTR_NO_NAME = 'A name must be specified'
EXPSTR_INVALID_NAME = 'Item name is invalid'
EXPSTR_NO_PRICE = 'A price must be specified'


def parse_expstr(exp_string):
    tokens = exp_string.split(' ')

    tokens_with_type = []
    have_tokens = set()
    for token in tokens:
        tok_type = get_expstr_token_type(token, not_type=have_tokens)
        tok_type_len = len(tok_type)
        if tok_type_len == 0:
            pass
        elif tok_type_len == 1:
            tok_type = tok_type[0]
            have_tokens.update(tok_type)

        tokens_with_type.append((token, tok_type))

    tokens_with_type = _clean_tokens(tokens_with_type)

    name_tokens = []
    price = None
    for token, token_type in tokens_with_type:
        if token_type == 'name':
            name_tokens.append(token)
        elif token_type == 'price':
            price = token

    return {
        'name': ' '.join(name_tokens),
        'price': price,
    }


def _clean_tokens(tokens_with_type):
    name_token_indices = [
        idx for idx, tok in enumerate(tokens_with_type) if tok[1] == 'name'
    ]

    name_token_indices_len = len(name_token_indices)
    if name_token_indices_len == 0:
        raise ExpstrError(name=EXPSTR_NO_NAME)

    expected_indices = list(range(0, 0 + name_token_indices_len))
    if name_token_indices != expected_indices:
        raise ExpstrError(name=EXPSTR_INVALID_NAME)

    cleaned = tokens_with_type[0:name_token_indices_len]

    for token, token_type in tokens_with_type:
        if token_type == 'price' or 'price' in token_type:
            cleaned.append((
                _get_price_value_from_token(token),
                'price'
            ))

    final_token_types = [token_type for token, token_type in cleaned]
    if 'price' not in final_token_types:
        raise ExpstrError(price=EXPSTR_NO_PRICE)

    return cleaned


def _get_price_value_from_token(token):
    match = re.search(explicit_price_token_regex, token)
    if match:
        return float(match.group(1))

    match = re.search(number_2dec_token_regex, token)
    if match:
        return float(match.group(0))

    raise ValueError('Invalid token')


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
