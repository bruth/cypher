from __future__ import unicode_literals, absolute_import

from .token import Token

# Math
ADD = Token('+')
SUB = Token('-')
MUL = Token('*')
DIV = Token('/')
MOD = Token('%')
POW = Token('^')

# Comparison
EQ = Token('=')
NEQ = Token('<>')
LT = Token('<')
GT = Token('>')
LTE = Token('<=')
GTE = Token('>=')

# Boolean
AND = Token('AND')
OR = Token('OR')
XOR = Token('XOR')
NOT = Token('NOT')

# Regex
REGEXP = Token('=~')

# String/collection
CONCAT = Token('+')

# Collection
IN = Token('IN')

# Operator sets
math = {ADD, SUB, MUL, DIV, MOD, POW}
comparison = {EQ, NEQ, LT, GT, LTE, GTE}
boolean = {AND, OR, XOR, NOT}
regexp = {REGEXP}
string = {CONCAT}
collection = {CONCAT, IN}

# All operators
operators = math | comparison | boolean | regexp | string | collection
