from rdflib import Graph, Namespace, RDF, RDFS
import os
import sys

def create_tbox_graph():
    g = Graph()
    EX = Namespace("http://example.org/")
    g.bind("ex", EX)

    # === Classes ===
    classes = [
        "Author", "Paper", "Conference", "Workshop",
        "Journal", "Keyword", "Review"
    ]
    for cls in classes:
        g.add((EX[cls], RDF.type, RDFS.Class))

    # === Object Properties ===
    object_props = {
        "authorOf": ("Author", "Paper"),
        "correspondingAuthor": ("Author", "Paper"),
        "about": ("Paper", "Keyword"),
        "publishedInConference": ("Paper", "Conference"),
        "publishedInWorkshop": ("Paper", "Workshop"),
        "publishedInJournal": ("Paper", "Journal"),
        "related": ("Paper", "Paper"),
        "reviews": ("Review", "Paper"),
        "wroteReview": ("Author", "Review"),
    }
    for prop, (domain, range_) in object_props.items():
        g.add((EX[prop], RDF.type, RDF.Property))
        g.add((EX[prop], RDFS.domain, EX[domain]))
        g.add((EX[prop], RDFS.range, EX[range_]))

    # === Datatype Properties ===
    datatype_props = {
        "hasTitle": "Paper",
        "hasAbstract": "Paper",
        "hasYear": "Paper",
        "hasDOI": "Paper",
        "fullName": "Author",
        "affiliatedTo": "Author",
        "keywordName": "Keyword",
        "hasVolume": "Journal",
        "reviewComment": "Review",
        "reviewScore": "Review",
    }
    for prop, domain in datatype_props.items():
        g.add((EX[prop], RDF.type, RDF.Property))
        g.add((EX[prop], RDFS.domain, EX[domain]))
        g.add((EX[prop], RDFS.range, RDFS.Literal))

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
