from __future__ import unicode_literals, absolute_import

import re

try:
    str = unicode
except NameError:
    pass

from . import constants, utils
from .token import Token


class Value(Token):
    def __init__(self, value):
        self.value = value

    def tokenize(self):
        value = self.value

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
        if isinstance(value, Identifier):
            alias = value.alias
            identifier = value.identifier
            value = value.value
        elif hasattr(value, 'identifier'):
            value = value.identifier

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
    def __init__(self, function, arguments=None, alias=None):
        if not arguments:
            arguments = []
        elif not isinstance(arguments, (list, tuple)):
            arguments = [arguments]

        self.function = function
        self.arguments = arguments
        self.alias = alias

    def tokenize(self):
        toks = [self.function, '(']
        toks.extend(utils.delimit(self.arguments, ', '))
        toks.append(')')

        if self.alias:
            toks.extend([' ', constants.AS, ' ', Identifier(self.alias)])

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
        if identifier is None and hasattr(props, 'identifier'):
            identifier = props.identifier

        if hasattr(props, 'props'):
            props = props.props

        self.props = props
        self.identifier = identifier

    def tokenize(self):
        toks = []

        if self.identifier:
            toks.extend([Identifier(self.identifier), ' = '])

        toks.append('{')

        toks.extend(utils.delimit([
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
        toks = []

        for value in self.values:
            if not isinstance(value, Token):
                value = Value(value)

            toks.append(value)

        if self.delimiter is None:
            return toks

        return utils.delimit(toks, delimiter=self.delimiter)


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
    def __init__(self, start=None, type=None, end=None, identifier=None,
                 props=None, reverse=False, directed=True):
        self.start = start
        self.type = type
        self.end = end
        self.identifier = identifier
        self.props = props
        self.reverse = reverse
        self.directed = directed

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

        if self.directed and self.reverse is True:
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
                    toks.append(':')
                    types = [Identifier(t) for t in self.type]
                    toks.extend(utils.delimit(types, delimiter='|'))
                elif self.type.startswith('*'):
                    toks.append(self.type)
                else:
                    toks.extend([':', Identifier(self.type)])

            if self.props:
                if space:
                    toks.append(' ')

                toks.append(Map(self.props))

            toks.append(']')

        if self.directed and self.reverse is False:
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
        if identifier is None and hasattr(props, 'identifier'):
            identifier = props.identifier

        if hasattr(props, 'props'):
            props = props.props

        self.props = props
        self.identifier = identifier

    def tokenize(self):
        return utils.delimit([
            Property(k, v, self.identifier) for k, v in self.props.items()
        ])


class Predicate(Token):
    def __init__(self, subject, operator=None, value=None, alias=None):
        self.subject = subject
        self.operator = operator
        self.value = value
        self.alias = alias

    def tokenize(self):
        if hasattr(self.subject, 'identifier'):
            subject = Identifier(self.subject.identifier)
        else:
            subject = Value(self.subject)

        toks = [subject]

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
        toks.extend(utils.delimit(self.preds, delimiter=delimiter))

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

    def __init__(self, values, unique=False):
        self.unique = unique
        super(Create, self).__init__(values)

    def tokenize(self):
        toks = [self.keyword, ' ']

        if self.unique:
            toks.extend([' ', 'UNIQUE', ' '])

        toks.extend(ValueList.tokenize(self))

        return toks


class CreateUnique(Create):
    def __init__(self, values):
        super(CreateUnique, self).__init__(values, unique=True)


class CreateIndex(Statement):
    keyword = 'CREATE INDEX'

    def __init__(self, label, prop):
        self.label = label
        self.prop = prop

    def tokenize(self):
        return [self.keyword, ' ', ':', Identifier(self.label),
                '(', Identifier(self.prop), ')']


class DropIndex(CreateIndex):
    keyword = 'DROP INDEX'


class CreateConstraint(Statement):
    keyword = 'CREATE CONSTRAINT'

    def __init__(self, label, prop):
        self.label = label
        self.prop = prop

    def tokenize(self):
        n = Node(labels=[self.label], identifier='n')

        return [self.keyword, ' ', 'ON', ' ', n, ' ', 'ASSERT', ' ',
                Predicate(Identifier(self.prop, identifier='n'), 'IS UNIQUE')]


class DropConstraint(CreateConstraint):
    keyword = 'DROP CONSTRAINT'


class Delete(Statement, ValueList):
    keyword = 'DELETE'


class Skip(Statement):
    keyword = 'SKIP'

    def __init__(self, value):
        if not isinstance(value, int):
            raise TypeError('SKIP value must be an integer')

        self.value = value


class Limit(Statement):
    keyword = 'LIMIT'

    def __init__(self, value):
        if not isinstance(value, int):
            raise TypeError('LIMIT value must be an integer')

        self.value = value


class OrderBy(Statement, ValueList):
    keyword = 'ORDER BY'


class Return(Statement, ValueList):
    keyword = 'RETURN'

    def __init__(self, values, distinct=False):
        self.distinct = distinct
        super(Return, self).__init__(values)

    def tokenize(self):
        toks = [self.keyword, ' ']

        if self.distinct:
            toks.extend(['DISTINCT', ' '])

        values = []

        for value in self.values:
            # Use the identifier of nodes, rels, and paths if defined
            if isinstance(value, (Node, Rel, Path)) and value.identifier:
                value = Identifier(value.identifier)
            elif not isinstance(value, Token):
                value = Value(value)

            values.append(value)

        toks.extend(utils.delimit(values, delimiter=self.delimiter))

        return toks


class ReturnDistinct(Return):
    def __init__(self, values):
        super(ReturnDistinct, self).__init__(values, distinct=True)


class With(Statement, ValueList):
    keyword = 'WITH'

    def tokenize(self):
        toks = [self.keyword]
        values = []

        for value in self.values:
            # Use the identifier of nodes, rels, and paths if defined
            if isinstance(value, (Node, Rel, Path)) and value.identifier:
                value = Identifier(value.identifier)
            elif not isinstance(value, Token):
                value = Value(value)

            values.append(value)

        toks.extend(utils.delimit(values, delimiter=self.delimiter))

        return toks


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
        return utils.delimit(self.tokens, delimiter=self.delimiter)
