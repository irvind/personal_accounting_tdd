import re


name_token_regex = r'^.+$'
price_token_regex = r'^(\d+(?:\.\d{1,2})?)(?:р|руб\.?)?$'
# quantity_token_regex = (
#     r'(?:(<>[xXхХ])\d+|'
#     r'\d+(?:\.\d+)(кг|г|л|мл)'
#     r'(\d|1\d|2\d)'
# )


def parse_expstr(exp_string):
    tokens = exp_string.split(' ')

    tokens_with_type = []
    for token in tokens:
        types = get_expstr_token_type(token)

    tokens_with_type = [(token, get_expstr_token_type()) for token in tokens]

    pass


def get_expstr_token_type(token):
    if re.search(name_token_regex, token):
        return ('name',)



# token stream
# first tokens - item name

# \d+(?:\.\d{1,2})?(?:р|руб\.?)?
#   12.43 12р 456.45руб 1руб. 6875

# [xх]\d+ , \d+(?:\.\d+)(кг|г|л|мл) , (\d|1\d|2\d)
