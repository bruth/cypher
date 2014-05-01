from __future__ import unicode_literals

# Math
ADD = '+'
SUB = '-'
MUL = '*'
DIV = '/'
MOD = '%'
POW = '^'

# Comparison
EQ = '='
NEQ = '<>'
LT = '<'
GT = '>'
LTE = '<='
GTE = '>='

# Boolean
AND = 'AND'
OR = 'OR'
XOR = 'XOR'
NOT = 'NOT'

# Regex
REGEXP = '=~'

# String/collection
CONCAT = '+'

# Collection
IN = 'IN'

# Operator sets
math = {ADD, SUB, MUL, DIV, MOD, POW}
comparison = {EQ, NEQ, LT, GT, LTE, GTE}
boolean = {AND, OR, XOR, NOT}
regexp = {REGEXP}
string = {CONCAT}
collection = {CONCAT, IN}

# All operators
operators = math | comparison | boolean | regexp | string | collection
