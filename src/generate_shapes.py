import sys
from rdflib import Graph, Namespace, RDF, RDFS, OWL, BNode, URIRef
from rdflib.namespace import SH, XSD

# Usage: python generate_shapes.py tbox.ttl shapes.ttl

def fragment(uri: URIRef) -> str:
    return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python generate_shapes.py <input_tbox.ttl> <output_shapes.ttl>")
        sys.exit(1)

    tbox_path = sys.argv[1]
    shapes_path = sys.argv[2]

    # Load TBox
    tbox = Graph()
    tbox.parse(tbox_path, format='turtle')

    # Prepare Shapes graph
    shapes = Graph()
    shapes.bind('sh', SH)
    shapes.bind('rdfs', RDFS)
    shapes.bind('owl', OWL)
    # preserve original ontology namespace prefixes
    for prefix, ns in tbox.namespaces():
        if prefix and ns not in (SH, RDFS, OWL, XSD):
            shapes.bind(prefix, ns)

    # Collect properties by domain
    domain_map = {}  # class URIRef -> list of property URIRef
    for prop, _, domain in tbox.triples((None, RDFS.domain, None)):
        domain_map.setdefault(domain, []).append(prop)

    # Collect range for each property
    range_map = {}   # property URIRef -> range URIRef
    for prop, _, rng in tbox.triples((None, RDFS.range, None)):
        range_map[prop] = rng

    # Create a NodeShape per domain class
    for cls, props in domain_map.items():
        # Create a shape node: ex:ClassNameShape
        cls_frag = fragment(str(cls))
        shape_node = Namespace(cls.split('#')[0] + '#')[f'{cls_frag}Shape']
        shapes.add((shape_node, RDF.type, SH.NodeShape))
        shapes.add((shape_node, SH.targetClass, cls))

        # Add a sh:property for each property
        for prop in props:
            prop_node = BNode()
            shapes.add((shape_node, SH.property, prop_node))
            shapes.add((prop_node, SH.path, prop))
            # If prop has a declared range, enforce class or datatype
            if prop in range_map:
                rng = range_map[prop]
                # Check if rng is a datatype
                if isinstance(rng, URIRef) and rng.startswith(str(XSD)):
                    shapes.add((prop_node, SH.datatype, rng))
                else:
                    shapes.add((prop_node, SH['class'], rng))

    # Serialize shapes graph
    shapes.serialize(destination=shapes_path, format='turtle')
    print(f"SHACL shapes written to {shapes_path}")
