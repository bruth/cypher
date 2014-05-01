# Cypher

The goal of the API is to serve as a foundation for building *simpler* domain-specific APIs. If nothing else, it prevents needing to use string formatting or concentation for building a Cypher statement programmatically.

## Examples

**Node**

```python
from cypher import *

Node({'id': 1}, identifier='n', labels=['Foo', 'Bar'])
```

**Result**

```cypher
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

```cypher
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

```cypher
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
- Delete
- Return
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
