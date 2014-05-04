from __future__ import unicode_literals


class Token(object):
    def __init__(self, value):
        self.value = value

    def tokenize(self):
        return [self.value]

    def __str__(self):
        return ''.join([str(t) for t in self.tokenize()])

    def __eq__(self, other):
        if not isinstance(other, (Token, str)):
            return False
        return str(self) == str(other)

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return str(self)
