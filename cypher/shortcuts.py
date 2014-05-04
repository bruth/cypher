from __future__ import unicode_literals, absolute_import
from .syntax import *  # noqa


def exists(value):
    "Query to test if a value exists."
    if not isinstance(value, Token):
        raise TypeError('value must be a token')

    if not hasattr(value, 'identifier'):
        raise TypeError('value must support an identifier')

    if not value.identifier:
        value = value.__class__(**value.__dict__)
        value.identifier = 'v'

    ident = Identifier(value.identifier)

    return Query([
        OptionalMatch(value),
        Return(Predicate(ident, 'IS NOT NULL')),
        Limit(1),
    ])


def get(value):
    "Query to get the value."
    if not isinstance(value, Token):
        raise TypeError('value must be a token')

    if not hasattr(value, 'identifier'):
        raise TypeError('value must support an identifier')

    if not value.identifier:
        value = value.__class__(**value.__dict__)
        value.identifier = 'v'

    ident = Identifier(value.identifier)

    return Query([
        Match(value),
        Return(ident)
    ])
