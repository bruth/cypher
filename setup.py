from setuptools import setup
from cypher import __version__

kwargs = {
    'packages': ['cypher'],
    'include_package_data': True,
    'name': 'cypher',
    'version': __version__,
    'author': 'Byron Ruth',
    'author_email': 'b@devel.io',
    'description': 'Neo4j Cypher compiler for building domain-specific APIs',
    'license': 'BSD',
    'keywords': 'neo4j cypher compiler',
    'url': 'https://github.com/bruth/cypher/',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
}

setup(**kwargs)
