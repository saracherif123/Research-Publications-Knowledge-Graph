from rdflib import Graph, Namespace, RDF, RDFS
import os
import sys

def create_tbox_graph():
    g = Graph()
    EX = Namespace("http://example.org/schema#")
    g.bind("ex", EX)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)

    # === Classes ===
    classes = ['Abstract', 'AcademicPublisher', 'Author', 'Conference',
               'Event', 'IsCorrespondingAuthorOf', 'Journal', 'Keyword', 'Magazine',
               'Paper', 'PaperCollection', 'Proceeding', 'Reviewer', 'Workshop','Venue','Year']
    for cls in classes:
        g.add((EX[cls], RDF.type, RDFS.Class))

    # === Object Properties ===
    object_props = {
        "cites": ("Paper", "Paper"),           # A paper can cite another paper
        "discusses": ("Paper", "Keyword"),      # A paper can discuss a keyword
        "hasVenue": ("Event", "Venue"),        # An event has a venue
        "hasYear": ("Event", "Year"),          # An event has a year
        "includes": ("PaperCollection", "Paper"), # A paper collection includes papers
        "publisedAt": ("Paper", "PaperCollection"), # A paper is published in a collection
        "reviews": ("Reviewer", "Paper"),      # A reviewer reviews a paper
        "summarizedBy": ("Paper", "Abstract"), # A paper is summarized by an abstract
        "writes": ("Author", "Paper")          # An author writes a paper
    }
    for prop, (domain, range_) in object_props.items():
        g.add((EX[prop], RDF.type, RDF.Property))
        g.add((EX[prop], RDFS.domain, EX[domain]))
        g.add((EX[prop], RDFS.range, EX[range_]))

    # === Subclass Relationships ===
    subclasses = {
        "Conference": "Event",
        "Workshop": "Event",
        "Journal": "PaperCollection",
        "Conference": "PaperCollection",
        "Workshop": "PaperCollection",
        "Proceeding": "AcademicPublisher",
        "Magazine": "AcademicPublisher"
    }
    for subclass, superclass in subclasses.items():
        g.add((EX[subclass], RDFS.subClassOf, EX[superclass]))

    return g

def save_graph(graph: Graph, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    graph.serialize(destination=path, format="turtle")
    print(f"TBOX saved to {path}")
    print(f"Graph contains {len(graph)} triples.")

if __name__ == "__main__":
    output_path = sys.argv[1] if len(sys.argv) > 1 else "output/tbox.ttl"
    g = create_tbox_graph()
    save_graph(g, output_path)
