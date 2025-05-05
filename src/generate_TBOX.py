# src/B1_generate_tbox.py

from rdflib import Graph, Namespace, RDF, RDFS
import os
import sys

# Create graph
g = Graph()
EX = Namespace("http://example.org/")
g.bind("ex", EX)

# Define Classes
classes = [
    "Author", "Paper", "Conference", "Workshop", "Journal", "Keyword", "Review"
]
for cls in classes:
    g.add((EX[cls], RDF.type, RDFS.Class))

# Define Object Properties
object_props = {
    "authorOf": ("Author", "Paper"),
    "correspondingAuthor": ("Author", "Paper"),
    "about": ("Paper", "Keyword"),
    "publishedInConference": ("Paper", "Conference"),
    "publishedInWorkshop": ("Paper", "Workshop"),
    "publishedInJournal": ("Paper", "Journal"),
    "related": ("Paper", "Paper"),
    "reviews": ("Review", "Paper"),
    "wroteReview": ("Author", "Review")
}
for prop, (domain, range_) in object_props.items():
    g.add((EX[prop], RDF.type, RDF.Property))
    g.add((EX[prop], RDFS.domain, EX[domain]))
    g.add((EX[prop], RDFS.range, EX[range_]))

# Define Datatype Properties
datatype_props = {
    "hasTitle": "Paper",
    "hasAbstract": "Paper",
    "hasYear": "Paper",
    "hasDOI": "Paper"
}
for prop, domain in datatype_props.items():
    g.add((EX[prop], RDF.type, RDF.Property))
    g.add((EX[prop], RDFS.domain, EX[domain]))
    g.add((EX[prop], RDFS.range, RDFS.Literal))

# Determine output path
if len(sys.argv) > 1:
    output_path = sys.argv[1]
else:
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "tbox.ttl")

# Serialize and save
g.serialize(destination=output_path, format="turtle")
print(f"TBOX saved to {output_path}")
