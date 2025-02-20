import json
import os
import pathlib
from typing import Optional
from urllib.parse import urlparse

import rdflib

#===================

def relative_path(path: str | pathlib.Path) -> bool:
    return str(path).split(':', 1)[0] not in ['file', 'http', 'https']

def make_uri(path: str | pathlib.Path) -> str:
    return pathlib.Path(os.path.abspath(path)).as_uri() if relative_path(path) else str(path)

def pathlib_path(path: str) -> pathlib.Path:
    return pathlib.Path(urlparse(path).path)

#===================

type PrefixDict = dict[str, str]

class Prefixer:
    def __init__(self, prefixes: Optional[PrefixDict]=None):
        if prefixes is not None:
            self.__prefix_dict = prefixes
        else:
            self.__prefix_dict = {}

    @property
    def sparql_prefixes(self) -> str:
        return '\n'.join([f'PREFIX {pfx} <{uri}>' for (pfx, uri) in self.__prefix_dict.items()])

    def add_uri(self, prefix: str, url: str):
        self.__prefix_dict[prefix] = url

    def curie(self, full_uri: str) -> str:
        for (pfx, uri) in self.__prefix_dict.items():
            if full_uri.startswith(uri):
                return f'{pfx}{full_uri[len(uri):]}'
        return full_uri

#===================

class Template:

    def instantiate(self, ):
        pass

#===================


#===================

PREFIX_DICT: PrefixDict = {
    'bg:': 'http://celldl.org/ontologies/bond-graph#',
    'cdt:': 'https://w3id.org/cdt/',
    'lib:': 'http://celldl.org/templates/vascular#',
    'tpl:': 'http://celldl.org/ontologies/model-template#',
}

#===================

def query_rdf(graph: rdflib.Graph, prefixer: Prefixer, sparql: str, keys: list[str]):
    print(', '.join(keys))
    for row in graph.query(f'{prefixer.sparql_prefixes}\n{sparql}'):
        result_dict = row.asdict()      # type: ignore
        print(', '.join([f'"{prefixer.curie(result_dict[key])}"' for key in keys]))

#===================

class Model:
    def __init__(self, model_path: str, prefix_dict: PrefixDict):
        self.__graph = rdflib.Graph()
        self.__graph.parse(model_path, format='turtle')
        self.__prefixer = Prefixer(prefix_dict)
        self.__prefixer.add_uri(':', f'{make_uri(model_path)}#')

    def query(self, sparql: str, keys: list[str]):
        print(', '.join(keys))
        for row in self.__graph.query(f'{self.__prefixer.sparql_prefixes}\n{sparql}'):
            result_dict = row.asdict()      # type: ignore
            print(', '.join([f'"{self.__prefixer.curie(result_dict[key])}"' for key in keys]))

#===================

def main(model_path: str):
#=========================

    model = Model(model_path, PREFIX_DICT)
    model.query(f'''
SELECT ?model ?tpl ?conn ?port ?node
{{
    ?model a bg:Model .
    ?model bg:component ?component .
    ?component tpl:template ?tpl .
    ?component tpl:connection ?conn .
    ?conn tpl:port ?port .
    ?comm bg:node ?node .
}} ORDER BY ?model ?tpl ?node
''', ['model', 'tpl', 'conn', 'port', 'node'])


#===================

if __name__ == '__main__':
    main('models/stomach-spleen.ttl')

#===================
