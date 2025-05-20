from rdflib import Graph
from pyshacl import validate

# 1) load your TBox-derived shapes
shapes = Graph().parse('output/tbox.ttl', format='turtle')

# 2) load the generated ABox
data   = Graph().parse('output/abox.ttl', format='turtle')

# 3) validate
conforms, report_graph, report_text = validate(
    data_graph=data,
    shacl_graph=shapes,
    inference='rdfs',       # if you want to use subclass inference
    abort_on_first=False,   # collect all errors
    meta_shacl=False,
    advanced=True
)

print(report_text)
if not conforms:
    raise SystemExit("❌ ABox does _not_ conform to TBox shapes")
else:
    print("✅ ABox conforms!")
