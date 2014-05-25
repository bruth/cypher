# Cypher

The goal of the API is to serve as a foundation for building *simpler* domain-specific APIs. If nothing else, it prevents needing to use string formatting or concatenation for building a Cypher statement programmatically.

## Examples

**Node**

```python
from cypher import *

Node({'id': 1}, identifier='n', labels=['Foo', 'Bar'])
```

**Result**

```
(n:Foo:Bar {id: 1})
```

**Match Path**

```python
rel1 = Rel(Node(), Node({'name': 'Bob'}), 'FRIENDS')
rel2 = Rel(rel1.end, Node({'name': 'Sue'}), '*1..3', reverse=True)
path = Path([rel1, rel2], identifier='p')

Query([
    Match(path),
    Return(Identifier(path.identifier)),
])
```

**Result**

```
MATCH p = ()-[:FRIENDS]->({name: 'Bob'})<-[*1..3]-({name: 'Sue'})
RETURN p
```

**Merge Relationship**

```python
charlie = Node({'name': 'Charlie Sheen'}, identifier='charlie', labels=['Person'])
oliver = Node({'name': 'Oliver Stone'}, identifier='oliver', labels=['Person'])

knows = Rel(charlie, oliver, 'KNOWS', identifier='knows')

Query([
    Merge(knows),
    Return([
        Identifer(charlie.identifier),
        Identifer(oliver.identifier),
        Identifer(knows.identifier),
    ]),
])
```

**Result**

```
MERGE (charlie:Person {name: 'Charlie Sheen'})-[r:KNOWS]->(oliver:Person {name: 'Oliver Stone'})
RETURN DISTINCT  c, o, r
```

**Conditional Match**

```python
gene = Node({'name': 'Gene Hackman'}, identifier='gene')
movie = Node(identifier='movie')
n = Node(identifier='n')

acted_in = Rel(gene, movie, 'ACTED_IN')
other_in = Rel(movie, n, 'ACTED_IN', reverse=True)
path = Path([acted_in, other_in])

directed = Rel(n, Node(), 'DIRECTED')

match = Match(path)
where = Where(directed)
ret = Return(Property('name', identifier='n'), distinct=True)

Query([match, where, ret])
```

**Result**

```python
MATCH (gene {name: 'Gene Hackman'})-[:ACTED_IN]->(movie)<-[:ACTED_IN]-(n)
WHERE (n)-[:DIRECTED]->()
RETURN DISTINCT n.name
```

## Status

- Alpha in API design
- Incomplete set of token classes
    - Undecided with how granular the API needs to be
- No protection against wrong types
- **Contributions to the overall approach, design, or code are welcome!**

## Supported Syntax

*API docs coming soon!*

- Value
- Identifer
- Function
- Map
- Collection
- Node
- Rel
- Path
- Property
- PropertyList
- Predicate
- PredicateList
- Start
- Where
- Match
- OptionalMatch
- Create
- CreateUnique
- Delete
- Return
- ReturnDistinct
- Skip
- Limit
- OrderBy
- With
- Merge
- OnCreate
- OnMatch
- Set
- Union
- UnionAll
- Query
- StartNode
- StartRel


## Docs

### Value

Converts a Python value into a Cypher equivalent string. If a value is passed that is already a `Token` instance, it will pass through. Lists, tuples, and dicts are wrapped in their respective token classes (`Collection` and `Map`).

```python
>>> Value(True)
TRUE
>>> Value(False)
FALSE
>>> Value(None)
NULL
>>> Value({'a': 1})
{a: 1}
>>> Value([1, 'a'])
[1, 'a']
>>> Value(b'foo')
'foo'
>>> Value(u'foo')
'foo'
>>> Value('foo')
'foo'
```

### Identifer

Takes a string and outputs a valid Cypher identifier by wrapping it in backticks if necessary.

```python
>>> Identifier('a b'))
`a b`

# Auto-extraction of object identifiers
>>> node = Node(identifier='joe')
>>> Identifier(node)
joe

# A map property can be represented
>>> Identifier('name', identifier='joe')
n.name

# Alias to the identifier
>>> Identifier('n', alias='joe')
n AS joe
```

### Function

Takes a function name and one or more arguments.

```python
>>> Function(ROUND, 1.54)
round(1.54)

# Alias to the identifier
>>> Function(ROUND, 1.54, alias='rounded')
round(1.54) AS rounded
```

### Node

Node pattern.

```python
# Bare
>>> Node()
()

# Properties
>>> Node({'a': 1})
({a: 1})

# Identifier
>>> Node({'a': 1}, identifier='n')
(n {a: 1})

# Labels
>>> Node({'a': 1}, identifier='n', labels=['Person'])
(n:Person {a: 1})
```

### Rel

Relationship pattern.

```python
# Bare
>>> Rel()
()-->()

# Reverse
>>> Rel(reverse=True)
()<--()

# Not directed
>>> Rel(directed=False)
()--()

# Identifiers
>>> Rel('a', 'TO', 'b')
(a)-[:TO]->(b)

# Properties
>>> Rel(type='TO', props={'foo': 1})
()-[:TO {foo: 1}]->()

# Variable length relationship
>>> Rel(type='*1..3')
()-[*1..3]->()

# Multiple types
>>> Rel(type=['TO', 'FROM'])
()-[:TO|FROM]-()

# Nodes
>>> a = Node({'label': 'A'}, identifier='a')
>>> b = Node({'label': 'B'}, identifier='b')
>>> Rel(a, 'TO', b)
(a {label: 'A'})-[:TO]->(b {label: 'B'})
```

### Path

Path pattern.

```python
>>> Path()
```

### StartNode/StartRel

Lookup for node or relationship in the START statement.

```python
>>> StartNode(10, identifier='n')
n=node(10)

# Multiple ints
>>> StartNode([10, 20], identifier='n')
n=node(10,20)

# Index; pass key and value rather than int
>>> StartNode('name', 'Joe', identifier='joe', index='names')
joe=node:names(name='Joe')
```


