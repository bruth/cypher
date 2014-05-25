from __future__ import unicode_literals, absolute_import

from .token import Token
from .syntax import Identifier, Value, Function
from .utils import delimit

try:
    str = unicode
except NameError:
    pass


COALESCE = Token('coalesce')
TIMESTAMP = Token('timestamp')
ID = Token('id')
STR = Token('str')
REPLACE = Token('replace')
SUBSTRING = Token('substring')
LEFT = Token('left')
TRIM = Token('trim')
UPPER = Token('upper')
ABS = Token('abs')
RAND = Token('rand')
ROUND = Token('round')
SQRT = Token('sqrt')
SIGN = Token('sign')
SIN = Token('sin')
DEGREES = Token('degrees')
LOG10 = Token('log10')
NODE = Token('node')
REL = Token('rel')

functions = {
    COALESCE,
    TIMESTAMP,
    ID,
    STR,
    REPLACE,
    SUBSTRING,
    LEFT,
    TRIM,
    UPPER,
    ABS,
    RAND,
    ROUND,
    SQRT,
    SIGN,
    SIN,
    DEGREES,
    LOG10,
    NODE,
    REL,
}


class _StartLookup(Token):
    function = ''

    def __init__(self, key, value=None, index=None, identifier=None):
        if index:
            if not isinstance(key, (str, bytes)):
                raise TypeError('key must be a string for index lookup')
            if value is None:
                raise TypeError('value cannot be None for index lookup')
        elif not isinstance(key, (list, tuple)):
            key = [key]

        self.key = key
        self.value = value
        self.index = index
        self.identifier = identifier

    def tokenize(self):
        toks = []

        if self.identifier:
            toks.extend([self.identifier, '='])

        toks.append(self.function)

        if self.index:
            toks.extend([':', self.index, '(',
                         Identifier(self.key), '=', Value(self.value), ')'])
        else:
            toks.append('(')
            toks.extend(delimit(self.key, ','))
            toks.append(')')

        return toks


class StartNode(_StartLookup):
    function = NODE


class StartRel(_StartLookup):
    function = REL


class Id(Function):
    def __init__(self, identifier):
        super(Id, self).__init__(ID, Identifier(identifier))
