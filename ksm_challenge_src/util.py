import demoji


class BiasedRandomFormat:
    def __init__(self, val):
        self._val = NumFormat(val[0])
        self._appraise = val[1]

    def __format__(self, format_spec: str):
        return format(self._val, format_spec) + f'({self._appraise})'


class NumFormat:
    def __init__(self, val: float):
        self._val = val

    def __format__(self, format_spec: str):
        if format_spec == '%':
            format_spec = '.0%'

        return format(self._val, format_spec or '.0f')


def recurrence(a_1: float, k: float, m: float, n: int) -> float:
    return (a_1 - m) * k ** (n - 1) + m * ((k ** n - 1) / (k - 1) if k != 1 else n)


def contains_emoji(s: str) -> bool:
    try:
        demoji.set_emoji_pattern()
    except IOError:
        demoji.download_codes()
    return bool(demoji.findall_list(s, desc=False))
