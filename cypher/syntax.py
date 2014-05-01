from __future__ import unicode_literals, absolute_import

import re

try:
    str = unicode
except NameError:
    pass

from . import constants


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


class Token(object):
    def tokenize(self):
        return []

    def __str__(self):
        return ''.join([str(t) for t in self.tokenize()])

    def __eq__(self, other):
        if not isinstance(other, (Token, str)):
            return False
        return str(self) == str(other)

    def __repr__(self):
        return str(self)


class Value(Token):
    def __init__(self, value, raw=False):
        self.value = value
        self.raw = raw

    def tokenize(self):
        value = self.value

        if self.raw:
            return [value]

        if value is True:
            value = constants.TRUE
        elif value is False:
            value = constants.FALSE
        elif value is None:
            value = constants.NULL
        elif isinstance(value, dict):
            value = Map(value)
        elif isinstance(value, (list, tuple)):
            value = Collection(value)
        elif isinstance(value, bytes):
            value = repr(value.decode()).lstrip('u')
        elif isinstance(value, str):
            value = repr(value).lstrip('u')

        return [value]


class Identifier(Token):
    "Represents an identifier or property identifier with an optional alias."
    valid_ident = re.compile(r'^[_a-z][_a-z0-0]*$', re.I)

    def __init__(self, value, identifier=None, alias=None):
        self.value = value
        self.identifier = identifier
        self.alias = alias

    def tokenize(self):
        toks = []

        if self.identifier:
            toks.extend([Identifier(self.identifier), '.'])

        # valid characters, no need to wrap in backticks
        if self.valid_ident.match(self.value):
            toks.append(self.value)
        else:
            toks.append('`{}`'.format(self.value))

        if self.alias:
            toks.extend([' AS ', Identifier(self.alias)])

        return toks


class Function(Token):
    def __init__(self, function, arguments=None):
        self.function = function
        self.arguments = arguments

    def tokenize(self):
        toks = [self.function, '(']
        toks.extend(delimit(self.arguments, ', '))
        toks.append(')')
        return toks


class MapPair(Token):
    "Represents a key/value pair in a map."
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def tokenize(self):
        return [Identifier(self.key), ': ', Value(self.value)]


class Map(Token):
    def __init__(self, props, identifier=None):
        self.props = props
        self.identifier = identifier

    def tokenize(self):
        toks = []

        if self.identifier:
            toks.extend([Identifier(self.identifier), ' = '])

        toks.append('{')

        toks.extend(delimit([
            MapPair(k, v) for k, v in self.props.items()
        ]))

        toks.append('}')

        return toks


class ValueList(Token):
    def __init__(self, values, delimiter=', '):
        if not isinstance(values, (list, tuple)):
            values = [values]

        self.values = values
        self.delimiter = delimiter

    def tokenize(self):
        return delimit([
            value if isinstance(value, Token) else Value(value)
            for value in self.values
        ])


class Collection(Token):
    def __init__(self, values, identifier=None):
        self.values = values
        self.identifier = identifier

    def tokenize(self):
        toks = []

        if self.identifier:
            toks.extend([Identifier(self.identifier), ' = '])

        toks.extend(['[', ValueList(self.values), ']'])

        return toks


class Node(Token):
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


class Rel(Token):
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

        start = self.start
        end = self.end

        if not isinstance(start, Token):
            start = Node(identifier=start)
        # Ensure this is an identifier or node
        elif not isinstance(self.start, (Identifier, Node)):
            raise ValueError('relationship start node must be an '
                             'identifier or node')

        if not isinstance(end, Token):
            end = Node(identifier=end)
        # Ensure this is an identifier or node
        elif not isinstance(self.end, (Identifier, Node)):
            raise ValueError('relationship end node must be an '
                             'identifier or node')

        toks.append(start)

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

        toks.append(end)

        return toks


class Path(Token):
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
            toks.extend([Identifier(self.identifier), ' = '])

        end = None

        for rel in self.rels:
            rtoks = rel.tokenize()

            if end is not None:
                start = rtoks.pop(0)

                if start != end:
                    raise ValueError('start is not the end')

            toks.extend(rtoks)
            end = rtoks[-1]

        return toks


class Property(Token):
    def __init__(self, key, value, identifier=None):
        self.key = key
        self.value = value
        self.identifier = identifier

    def tokenize(self):
        return [Identifier(self.key, identifier=self.identifier), ' = ',
                Value(self.value)]


class PropertyList(Token):
    def __init__(self, props, identifier=None):
        self.props = props
        self.identifier = identifier

    def tokenize(self):
        return delimit([
            Property(k, v, self.identifier) for k, v in self.props.items()
        ])


class Predicate(Token):
    def __init__(self, subject, operator=None, value=None, alias=None):
        self.subject = subject
        self.operator = operator
        self.value = value
        self.alias = alias

    def tokenize(self):
        toks = [self.subject]

        if self.operator:
            toks.extend([' ', self.operator])

        if self.value:
            toks.extend([' ', self.value])

        if self.alias:
            toks.extend([' AS ', Identifier(self.alias)])

        return toks


class PredicateList(Token):
    def __init__(self, preds, operator='AND'):
        self.preds = preds
        self.operator = operator

    def tokenize(self):
        toks = []

        if not self.preds:
            return toks

        if len(self.preds) == 1:
            toks.append(self.preds[0])
            return toks

        toks.append('(')

        delimiter = ' {} '.format(self.operator)
        toks.extend(delimit(self.preds, delimiter=delimiter))

        toks.append(')')

        return toks


class Statement(Token):
    keyword = ''

    def tokenize(self):
        toks = [self.keyword, ' ']
        toks.extend(super(Statement, self).tokenize())
        return toks


class Start(Statement, ValueList):
    keyword = 'START'


class Where(Statement, ValueList):
    keyword = 'WHERE'


class Match(Statement, ValueList):
    keyword = 'MATCH'


class OptionalMatch(Match):
    keyword = 'OPTIONAL MATCH'


class Create(Statement, ValueList):
    keyword = 'CREATE'


class Delete(Statement, ValueList):
    keyword = 'DELETE'


class Skip(Statement):
    keyword = 'SKIP'

    def __init__(self, skip):
        if not isinstance(skip, int):
            raise TypeError('SKIP value must be an integer')

        self.skip = skip

    def tokenize(self):
        return [self.keyword, ' ', self.skip]


class Limit(Statement):
    keyword = 'LIMIT'

    def __init__(self, limit):
        if not isinstance(limit, int):
            raise TypeError('LIMIT value must be an integer')

        self.limit = limit

    def tokenize(self):
        return [self.keyword, ' ', self.limit]


class OrderBy(Statement, ValueList):
    keyword = 'ORDER BY'


class Return(Statement, ValueList):
    keyword = 'RETURN'

    def __init__(self, exprs, distinct=False):
        self.distinct = distinct
        super(Return, self).__init__(exprs)

    def tokenize(self):
        toks = super(Return, self).tokenize()

        if self.distinct:
            toks.insert(1, ' DISTINCT ')

        return toks


class With(Statement, ValueList):
    keyword = 'WITH'


class Merge(Statement):
    keyword = 'MERGE'

    def __init__(self, expr):
        self.expr = expr

    def tokenize(self):
        return [self.keyword, ' ', self.expr]


class OnCreate(Statement, ValueList):
    keyword = 'ON CREATE'


class OnMatch(Statement, ValueList):
    keyword = 'ON MATCH'


class Set(Statement, ValueList):
    keyword = 'SET'


class Union(Statement):
    keyword = 'UNION'


class UnionAll(Statement):
    keyword = 'UNION ALL'


class Query(Token):
    def __init__(self, tokens, delimiter='\n'):
        self.tokens = tokens
        self.delimiter = delimiter

    def tokenize(self):
        return delimit(self.tokens, delimiter=self.delimiter)
