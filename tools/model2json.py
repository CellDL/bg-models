import json
import os
import pathlib
from typing import Optional
from urllib.parse import urlparse

#===================

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

type QueryResult = dict[str, str]

def sparql_query(graph: rdflib.Graph, prefixer: Prefixer, sparql: str, keys: list[str], trace=False) -> list[QueryResult]:
    sparql = f'{prefixer.sparql_prefixes}\n{sparql}'
    if trace:
        print(sparql)
        print()
        print(', '.join(keys))
    query_results: list[QueryResult] = []
    for row in graph.query(sparql):
        row_dict = row.asdict()      # type: ignore
        result = {key: prefixer.curie(row_dict[key]) for key in keys}
        query_results.append(result)
        if trace:
            print(', '.join(result.values()))
    return query_results

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

class Models:
    def __init__(self, model_path: str, prefix_dict: PrefixDict):
        self.__graph = rdflib.Graph()
        self.__graph.parse(model_path, format='turtle')
        self.__prefixer = Prefixer(prefix_dict)
        self.__prefixer.add_uri(':', f'{make_uri(model_path)}#')
        query_results = sparql_query(self.__graph, self.__prefixer, f'''
SELECT ?model ?component ?template ?port ?node
{{
    ?model
        a bg:Model ;
        bg:component ?component .
    ?component
        tpl:template ?template ;
        tpl:connection [
            tpl:port ?port ;
            bg:node ?node
        ]
}} ORDER BY ?model ?component ?tpl ?port ?node
''', ['model', 'component', 'template', 'port', 'node'])
        model_component_ports = []
        current_model = {}
        last_component = None
        for result_row in query_results:
            if result_row['model'] != current_model.get('model'):
                if len(current_model) and len(current_model['components']):
                    model_component_ports.append(current_model)
                current_model = {
                    'model': result_row['model'],
                    'components': []
                }
                last_component = None
            if last_component is not None and result_row['component'] != last_component.id:
                current_model['components'].append(last_component.as_dict())
                last_component = None
            if last_component is None:
                last_component = Component(result_row['component'], result_row['template'])
            last_component.add_port(result_row['port'], result_row['node'])
        if len(current_model):
            if last_component is not None:
                current_model['components'].append(last_component.as_dict())
            if len(current_model['components']):
                model_component_ports.append(current_model)
        self.__model_component_ports = model_component_ports

    @property
    def model_component_ports(self):
        return self.__model_component_ports

#===================

class Component:
    def __init__(self, id: str, template: str):
        self.__id = id
        self.__ports = []
        self.__template = template

    @property
    def id(self):
        return self.__id

    def add_port(self, port: str, node: str):
        self.__ports.append({
            'port': port,
            'node': node
        })

    def as_dict(self):
        return {
            'template': self.__template,
            'ports': self.__ports
        }

#===================

def main(model_path: str):
#=========================
    model = Models(model_path, PREFIX_DICT)
    print(json.dumps(model.model_component_ports, indent=4))

#===================

if __name__ == '__main__':
    main('models/stomach-spleen.ttl')

#===================
