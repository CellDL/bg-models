from rdflib import Graph


def jsonld2ttl(json_file: str, ttl_file: str):
#=============================================
    g = Graph()
    g.parse(json_file, format="json-ld")
    g.serialize(destination=ttl_file, format="turtle")

if __name__ == '__main__':
#=========================

    jsonld2ttl('data/main-resourceMap-c8a41ff6-7ca4-4ca4-a39d-fc0e313d7bb1.jsonld',
               'rdf/main-resourceMap.ttl')

    jsonld2ttl('data/main-resourceMap-flattened-c8a41ff6-7ca4-4ca4-a39d-fc0e313d7bb1.jsonld',
               'rdf/main-resourceMap-flattened.ttl')
