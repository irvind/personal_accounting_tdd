import re

from datetime import date

from .exceptions import ExpstrError
from .models import Expense


explicit_price_token_regex = r'^(\d+(?:\.\d{1,2})?)(?:р|руб\.?)$'
explicit_date_token_regex = r'^(\d|1\d|2\d|3[01]).([01]\d)(?:.(\d{4}))?д$'
implicit_full_date_token_regex = r'(\d|1\d|2\d|3[01]).([01]\d).(\d{4})$'
quantity_token_regex = (
    r'(?:[xXхХ](\d+)|(\d+)[xXхХ]|'
    r'(\d+(?:\.\d+)?)(кг|г|л|мл)\.?)'
)
number_2dec_token_regex = r'^\d+(\.\d{1,2})?$'
name_token_regex = r'^.+$'

EXPSTR_NO_NAME = 'A name must be specified'
EXPSTR_INVALID_NAME = 'Item name is invalid'
EXPSTR_NO_PRICE = 'A price must be specified'
EXPSTR_CANNOT_DETERMINE_PRICE = 'Cannot determine price'
EXPSTR_DUPLICATE_PRICE = 'Duplicated price'


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
            if tok_type != 'name':
                have_tokens.update(tok_type)

        tokens_with_type.append((token, tok_type))

    tokens_with_type = _clean_tokens(tokens_with_type)

    ret = {}
    name_tokens = []
    for token, token_type in tokens_with_type:
        if token_type == 'name':
            name_tokens.append(token)
        elif token_type in ('price', 'date', 'quantity'):
            ret[token_type] = token

    ret['name'] = ' '.join(name_tokens)

    return ret


def _clean_tokens(tokens_with_type):
    tokens_with_type = tokens_with_type[:]

    name_token_indices = [
        idx for idx, tok in enumerate(tokens_with_type) if tok[1] == 'name'
    ]

    name_token_indices_len = len(name_token_indices)
    if name_token_indices_len == 0:
        raise ExpstrError(name=EXPSTR_NO_NAME)

    expected_indices = list(range(0, 0 + name_token_indices_len))
    if name_token_indices != expected_indices:
        raise ExpstrError(name=EXPSTR_INVALID_NAME)

    token_types = [tok_type for _, tok_type in tokens_with_type]
    have_explicit_price = 'price' in token_types
    have_explicit_date = 'date' in token_types

    ambig_indices = [
        idx for idx, tok in enumerate(tokens_with_type)
        if tok[1] == ('price', 'date')
    ]

    have_price = have_explicit_price
    ambig_indices_len = len(ambig_indices)
    if ambig_indices_len > 0 and have_explicit_date and have_explicit_price:
        raise ExpstrError(price=EXPSTR_DUPLICATE_PRICE)
    if ambig_indices_len > 1:
        msg = (EXPSTR_CANNOT_DETERMINE_PRICE if not have_explicit_price
               else EXPSTR_DUPLICATE_PRICE)
        raise ExpstrError(price=msg)
    elif ambig_indices_len == 1:
        idx = ambig_indices[0]
        explicit_type = 'date' if have_explicit_price else 'price'
        tokens_with_type[idx] = (tokens_with_type[idx][0], explicit_type)

        if explicit_type == 'price':
            have_price = True

    if not have_price:
        raise ExpstrError(price=EXPSTR_NO_PRICE)

    cleaned = tokens_with_type[0:name_token_indices_len]

    _retrieval_map = {
        'price': _get_price_value_from_token,
        'date': _get_date_value_from_token,
        'quantity': _get_quantity_value_from_token,
    }
    for token, token_type in tokens_with_type[name_token_indices_len:]:
        cleaned_token = _retrieval_map[token_type](token)
        cleaned.append((cleaned_token, token_type))

    return cleaned


def _get_price_value_from_token(token):
    match = re.search(explicit_price_token_regex, token)
    if match:
        return float(match.group(1))

    match = re.search(number_2dec_token_regex, token)
    if match:
        return float(match.group(0))

    raise ValueError('Invalid token')


def _get_date_value_from_token(token):
    today_year = date.today().year
    match = re.search(explicit_date_token_regex, token)
    if match:
        args = [int(match.group(2)), int(match.group(1))]
        year_group = match.group(3)
        year = int(year_group) if year_group is not None else today_year
        args.insert(0, year)
        return date(*args)

    match = re.search(implicit_full_date_token_regex, token)
    if match:
        return date(
            int(match.group(3)),
            int(match.group(2)),
            int(match.group(1)),
        )

    match = re.search(number_2dec_token_regex, token)
    if match:
        day, month = match.group(0).split('.')
        return date(today_year, int(month), int(day))

    raise ValueError('Invalid token')


def _get_quantity_value_from_token(token):
    match = re.search(quantity_token_regex, token)
    if not match:
        raise ValueError('Invalid token')

    groups = match.groups()
    if groups[2] is not None:
        how_much, unit = groups[2], groups[3]
        return (
            'measurable',
            Expense.rus_unit_type_to_eng(unit),
            float(how_much)
        )
    else:
        how_many = int(
            groups[0] if groups[0] is not None else groups[1]
        )
        return ('countable', how_many)


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

    raise ValueError('Invalid token')
