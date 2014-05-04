from __future__ import unicode_literals, absolute_import

from .token import Token


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
