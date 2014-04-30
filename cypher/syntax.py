from __future__ import unicode_literals, absolute_import

import re

try:
    str = unicode
except NameError:
    pass


# Supported property value types:
# http://docs.neo4j.org/chunked/2.0.0/graphdb-neo4j-properties.html
VALID_TYPES = (bool, int, float, str, bytes)


FUNCTIONS = {
    'coalesce',
    'timestamp',
    'id',
    'str',
    'replace',
    'substring',
    'left',
    'trim',
    'upper',
    'abs',
    'rand',
    'round',
    'sqrt',
    'sign',
    'sin',
    'degress',
    'log10',
}


def cystr(value):
    "Creates a string representation of the passed value suitable for Cypher."
    if value is None:
        return 'NULL'

    if isinstance(value, bytes):
        return repr(value.decode()).lstrip('u')

    if isinstance(value, str):
        return repr(value).lstrip('u')

    if isinstance(value, bool):
        return 'true' if True else 'false'

    return value


class Token(object):
    def __init__(self, token):
        self.token = token

    def tokenize(self):
        return [self.token]

    def __str__(self):
        return ''.join([str(t) for t in self.tokenize()])

    def __repr__(self):
        return '<{}: "{}">'.format(self.__class__.__name__, str(self))


class Value(Token):
    pass


class Identifier(Token):
    ident_re = re.compile(r'^[_a-z][_a-z0-0]*$', re.I)

    def tokenize(self):
        if self.ident_re.match(self.token):
            return [self.token]
        return ['`{}`'.format(self.token)]


class Map(Value):
    def __init__(self, props, identifier=None):
        self.props = props
        self.identifier = identifier

    def tokenize(self):
        toks = []

        if self.identifier:
            toks.extend([Identifier(self.identifier), ' = '])

        toks.append('{')
        last = len(self.props) - 1

        for i, key in enumerate(self.props):
            value = self.props[key]

            # Nested map
            if isinstance(value, dict):
                value = Map(value)
            elif isinstance(value, (list, tuple)):
                value = Collection(value)
            else:
                value = cystr(value)

            toks.extend([Identifier(key), ': ', value])

            if i < last:
                toks.append(', ')

        toks.append('}')

        return toks


class Collection(Value):
    def __init__(self, values, identifier=None):
        self.values = values
        self.identifier = identifier

    def tokenize(self):
        toks = []

        if self.identifier:
            toks.extend([Identifier(self.identifier), ' = '])

        toks.append('[')
        last = len(self.props) - 1

        for i, value in enumerate(self.values):
            # Nested map
            if isinstance(value, dict):
                value = Map(value)
            elif isinstance(value, (list, tuple)):
                value = Collection(value)
            else:
                value = cystr(value)

            toks.append(value)

            if i < last:
                toks.append(', ')

        toks.append(']')

        return toks


class Node(Value):
    def __init__(self, props=None, identifier=None, labels=None):
        self.props = props
        self.identifier = identifier
        self.labels = labels

    def tokenize(self):
        toks = ['(']
        space = False

        if self.identifier:
            toks.append(Identifier(self.identifier))
            space = True

        if self.labels:
            toks.append(':')
            toks.append(':'.join(self.labels))
            space = True

        if self.props:
            if space:
                toks.append(' ')
            toks.append(Map(self.props))

        toks.append(')')

        return toks


class Rel(Value):
    def __init__(self, start, end, type=None, identifier=None,
                 props=None, reverse=False):
        self.start = start
        self.end = end
        self.type = type
        self.identifier = identifier
        self.props = props
        self.reverse = reverse

    def tokenize(self):
        toks = []

        toks.append(self.start)

        if self.reverse is True:
            toks.append('<-')
        else:
            toks.append('-')

        if self.identifier or self.type or self.props:
            toks.append('[')

            space = False

            if self.identifier:
                space = True
                toks.append(Identifier(self.identifier))

            if self.type:
                space = True

                if isinstance(self.type, (list, tuple)):
                    toks.append(':' + '|'.join(self.type))
                elif self.type.startswith('*'):
                    toks.append(self.type)
                else:
                    toks.append(':' + self.type)

            if self.props:
                if space:
                    toks.append(' ')

                toks.append(Map(self.props))

            toks.append(']')

        if self.reverse is False:
            toks.append('->')
        else:
            toks.append('-')

        toks.append(self.end)

        return toks


class Path(Value):
    """
    node, rel, node, rel, node...
    ()-->()<-[]-()
    """
    def __init__(self, rels, identifier=None):
        if not isinstance(rels, (list, tuple)):
            rels = [rels]

        self.rels = rels
        self.identifier = identifier

    def tokenize(self):
        toks = []

        if self.identifier:
            toks.append(Identifier(self.identifier))
            toks.append('=')

        end = None

        for rel in self.rels:
            rtoks = rel.tokenize()

            if end is not None:
                start = rtoks.pop(0)

                if start is not end:
                    raise ValueError('start is not the end')

            toks.extend(rtoks)
            end = rtoks[-1]

        return toks


class Expr(Value):
    expr_separator = ', '

    def __init__(self, exprs):
        if not isinstance(exprs, (list, tuple)):
            exprs = [exprs]

        self.exprs = exprs

    def tokenize(self):
        toks = []

        if not self.exprs:
            return toks

        last = len(self.exprs) - 1

        for i, e in enumerate(self.exprs):
            toks.append(e)

            if i < last:
                toks.append(self.expr_separator)

        return toks


class Property(Value):
    def __init__(self, key, value=None, identifier=None):
        self.key = key
        self.value = value
        self.identifier = identifier

    def tokenize(self):
        toks = []

        if self.identifier:
            toks.extend([Identifier(self.identifier), '.'])

        toks.append(Identifier(self.key))

        if self.value is not None:
            toks.extend([' = ', cystr(self.value)])

        return toks


class Properties(Expr):
    def __init__(self, props, identifier=None):
        self.props = props
        self.identifier = identifier

    def tokenize(self):
        toks = []
        last = len(self.props) - 1

        for i, key in enumerate(self.props):
            value = self.props[key]
            toks.append(Property(key, value, self.identifier))

            if i < last:
                toks.append(', ')

        return toks


class Predicate(Expr):
    def __init__(self, exprs, operator='AND'):
        super(Predicate, self).__init__(exprs)
        self.operator = operator

    def tokenize(self):
        toks = []

        if not self.exprs:
            return toks

        last = len(self.exprs) - 1

        if last == 0:
            toks.append(self.exprs[0])
            return toks

        toks.append('(')

        for i, pred in enumerate(self.exprs):
            toks.append(pred)

            if i < last:
                toks.append(' ')
                toks.append(self.operator)
                toks.append(' ')

        toks.append(')')

        return toks


class Statement(Expr):
    def tokenize(self):
        toks = [self.keyword, ' ']
        toks.extend(super(Statement, self).tokenize())
        return toks


class Start(Statement):
    keyword = 'START'


class Where(Statement):
    keyword = 'WHERE'


class Match(Statement):
    keyword = 'MATCH'


class OptionalMatch(Match):
    keyword = 'OPTIONAL MATCH'


class Create(Statement):
    keyword = 'CREATE'


class Delete(Statement):
    keyword = 'DELETE'


class Skip(Statement):
    keyword = 'SKIP'


class Limit(Statement):
    keyword = 'LIMIT'


class OrderBy(Statement):
    keyword = 'ORDER BY'


class Return(Statement):
    keyword = 'RETURN'

    def __init__(self, exprs, order_by=None, skip=None, limit=None,
                 distinct=False):
        super(Return, self).__init__(exprs)

        self.order_by = order_by
        self.skip = skip
        self.limit = limit
        self.distinct = distinct

    def tokenize(self):
        toks = super(Return, self).tokenize()

        toks.insert(1, ' DISTINCT ')

        if self.order_by:
            toks.extend([' ', self.order_by])

        if self.skip:
            toks.extend([' ', 'SKIP', ' ', self.skip])

        if self.limit is not None:
            toks.extend([' ', 'LIMIT', ' ', self.limit])

        return toks


class With(Statement):
    keyword = 'WITH'

    def __init__(self, exprs, order_by=None, skip=None, limit=None):
        super(With, self).__init__(exprs)

        self.order_by = order_by
        self.skip = skip
        self.limit = limit

    def tokenize(self):
        toks = super(With, self).tokenize()

        if self.order_by:
            toks.extend([' ', self.order_by])

        if self.skip:
            toks.extend([' ', 'SKIP', ' ', self.skip])

        if self.limit is not None:
            toks.extend([' ', 'LIMIT', ' ', self.limit])

        return toks


class Merge(Statement):
    keyword = 'MERGE'

    def __init__(self, expr, oncreate=None, onmatch=None):
        if oncreate and not isinstance(oncreate, (list, tuple)):
            oncreate = [oncreate]

        if onmatch and not isinstance(onmatch, (list, tuple)):
            onmatch = [onmatch]

        self.expr = expr
        self.oncreate = oncreate
        self.onmatch = onmatch

    def tokenize(self):
        toks = [self.keyword, ' ', self.expr]

        if self.oncreate:
            toks.append(' ')
            toks.append('ON CREATE SET')
            toks.append(' ')

            last = len(self.oncreate) - 1

            for i, e in enumerate(self.oncreate):
                toks.append(e)

                if i < last:
                    toks.append(', ')

        if self.onmatch:
            toks.append(' ')
            toks.append('ON MATCH SET')
            toks.append(' ')
            last = len(self.onmatch) - 1

            for i, e in enumerate(self.onmatch):
                toks.append(e)

                if i < last:
                    toks.append(', ')

        return toks


class Query(Expr):
    expr_separator = ' '
