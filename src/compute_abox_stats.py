from rdflib import Graph, RDF, RDFS, Namespace
from collections import Counter

# Load the ABOX TTL file
g = Graph()
g.parse("output/abox.ttl", format="ttl")

# Define your namespace
EX = Namespace("http://example.org/schema#")

# List of main classes to count
main_classes = [
    "Paper", "Author", "Reviewer", "Conference", "Workshop",
    "Journal", "Review", "Keyword", "Venue", "Translation", "Abstract"
]

# Initialize counters
class_counter = Counter()
object_props = set()
datatype_props = set()

# Count total triples
total_triples = len(g)

# Count instances of main classes
for s, p, o in g.triples((None, RDF.type, None)):
    if o.startswith(EX):
        class_label = o.split("#")[-1]
        if class_label in main_classes:
            class_counter[class_label] += 1

# Identify object vs. datatype properties
for s, p, o in g:
    if isinstance(o, str) or isinstance(o, int) or isinstance(o, float):
        datatype_props.add(p)
    elif (o, RDF.type, None) in g or (o, None, None) in g:
        object_props.add(p)

# Print results
print(f"Total RDF triples: {total_triples}")
print(f"Number of distinct classes instantiated: {len(class_counter)}")
print(f"Number of object properties used: {len(object_props)}")
print(f"Number of datatype properties used: {len(datatype_props)}")
print("\nClass instance counts:")
for cls in sorted(class_counter):
    print(f" - {cls}: {class_counter[cls]}")
