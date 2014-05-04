from __future__ import unicode_literals, absolute_import


def delimit(values, delimiter=', '):
    "Returns a list of tokens interleaved with the delimiter."
    toks = []

    if not values:
        return toks

    if not isinstance(delimiter, (list, tuple)):
        delimiter = [delimiter]

    last = len(values) - 1

    for i, value in enumerate(values):
        toks.append(value)

        if i < last:
            toks.extend(delimiter)

    return toks
