import re


def remove_extra_spaces(s):
    s = s.strip()
    s = re.sub(r'\s+', ' ', s)
    return s
