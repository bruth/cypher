# Cypher

The goal of the API is to serve as a foundation for building *simpler* domain-specific APIs. If nothing else, it prevents needing to use string formatting or concentation for building a Cypher statement programmatically.

## Examples

**Node**

```python
import cypher as c

c.Node({'id': 1}, identifier='n', labels=['Foo', 'Bar'])
```

**Result**

```cypher
(n:Foo:Bar {id: 1})
```

**MATCH**

```python
c.Match([
    c.Node(),
    c.Node({'id': 1}),
    c.Node({'id': 1}, labels=['Foo', 'Bar']),
])

```

**Result**

```cypher
MATCH (), ({id: 1}), (:Foo:Bar {id: 1})
```

**Complex 1**

```python
charlie = c.Node({'name': 'Charlie Sheen'}, identifier='charlie', labels=['Person'])
oliver = c.Node({'name': 'Oliver Stone'}, identifier='oliver', labels=['Person'])
knows = c.Rel(charlie, oliver, 'KNOWS', identifier='r')

c.Query([
    c.Merge(knows),
    c.With(['r', 'charlie AS c', 'oliver AS o']),
    c.Return('c, o, r', limit=1),
])
```

**Result**

```cypher
MERGE (charlie:Person {name: 'Charlie Sheen'})-[r:KNOWS]->(oliver:Person {name: 'Oliver Stone'}) WITH r, charlie AS c, oliver AS o RETURN DISTINCT  c, o, r LIMIT 1
```

**Complex 2**

```python
gene = c.Node({'name': 'Gene Hackman'}, identifier='gene')
movie = c.Node(identifier='movie')
n = c.Node(identifier='n')

acted_in = c.Rel(gene, movie, 'ACTED_IN')
other_in = c.Rel(movie, n, 'ACTED_IN', reverse=True)
path = c.Path([acted_in, other_in])

directed = c.Rel(n, c.Node(), 'DIRECTED')

match = c.Match(path)
where = c.Where(directed)
ret = c.Return(c.Property('name', identifier='n'), distinct=True)

c.Query([match, where, ret])
```

**Result**

```python
MATCH (gene {name: 'Gene Hackman'})-[:ACTED_IN]->(movie)<-[:ACTED_IN]-(n) WHERE (n)-[:DIRECTED]->() RETURN DISTINCT n.name
```

## Status

- Alpha in API design
- Incomplete set of token classes
    - Undecided with how granular the API needs to be
- No protection against wrong types
- **Contributions to the overall approach, design, or code are welcome!**

**Supported Syntax**

- Identifer
- Map
- Collection
- Node
- Rel
- Path
- Property
- Properties
- Predicate
- Start
- Where
- Match
- OptionalMatch
- Create
- Delete
- Return
- With
- Merge
- OrderBy
- Query
