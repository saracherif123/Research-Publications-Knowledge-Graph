import pandas as pd
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
import os

# === Setup ===
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

g = Graph()
EX = Namespace("http://example.org/schema#")
g.bind("ex", EX)
g.bind("rdfs", RDFS)

def uri(local):
    return EX[local]

# === Utility caches ===
_year_nodes = {}
_venue_nodes = {}
_abstract_nodes = {}

# === Helper to get or create Year individual ===
def get_year_node(year: int) -> URIRef:
    key = f"Year_{year}"
    if key not in _year_nodes:
        node = uri(key)
        g.add((node, RDF.type, EX.Year))
        # store year literal as rdfs:label
        g.add((node, RDFS.label, Literal(year)))
        _year_nodes[key] = node
    return _year_nodes[key]

# === Helper to get or create Venue individual ===
def get_venue_node(name: str) -> URIRef:
    key = f"Venue_{name.replace(' ', '_')}"
    if key not in _venue_nodes:
        node = uri(key)
        g.add((node, RDF.type, EX.Venue))
        g.add((node, RDFS.label, Literal(name)))
        _venue_nodes[key] = node
    return _venue_nodes[key]

# === Helper to get or create Abstract individual ===
def get_abstract_node(paper_id: str, text: str) -> URIRef:
    key = f"Abstract_{paper_id}"
    if key not in _abstract_nodes:
        node = uri(key)
        g.add((node, RDF.type, EX.Abstract))
        g.add((node, RDFS.label, Literal(text)))
        _abstract_nodes[key] = node
    return _abstract_nodes[key]

# === Load Papers ===
papers = pd.read_csv("data/papers.csv")
for _, row in papers.iterrows():
    pid = str(row['PaperId'])
    paper_node = uri(f"Paper_{pid}")
    g.add((paper_node, RDF.type, EX.Paper))
    # Abstract
    if pd.notna(row['Abstract']):
        abs_node = get_abstract_node(pid, row['Abstract'])
        g.add((paper_node, EX.summarizedBy, abs_node))
    # Year
    if pd.notna(row['Year']):
        yr = int(row['Year'])
        year_node = get_year_node(yr)
        # link via hasYear on Paper? TBOX domain Event but we treat PaperCollection separately
        g.add((paper_node, EX.hasYear, year_node))

# === Load Authors and author-paper relations ===
authors = pd.read_csv("data/nodes_authors.csv")
for _, row in authors.iterrows():
    aid = str(row['AuthorID'])
    author_node = uri(f"Author_{aid}")
    g.add((author_node, RDF.type, EX.Author))
    # Name stored as rdfs:label
    g.add((author_node, RDFS.label, Literal(row['Name'])))

# Writes relation (authorship)
rel_auth = pd.read_csv("data/rel_author_of.csv")
for _, row in rel_auth.iterrows():
    aid, pid = str(row['AuthorID']), str(row['PaperID'])
    g.add((uri(f"Author_{aid}"), EX.writes, uri(f"Paper_{pid}")))

# Corresponding authors as instances of IsCorrespondingAuthorOf
rel_corr = pd.read_csv("data/rel_corresponding_author.csv")
for idx, row in rel_corr.iterrows():
    aid, pid = str(row['AuthorID']), str(row['PaperID'])
    inst = uri(f"CorrAuth_{aid}_{pid}")
    # instance of class
    g.add((inst, RDF.type, EX.IsCorrespondingAuthorOf))
    # link to author and paper
    g.add((inst, EX.writes, uri(f"Paper_{pid}")))
    g.add((uri(f"Author_{aid}"), EX.writes, uri(f"Paper_{pid}")))  # maintain writes

# === Keywords and discusses ===
keywords = pd.read_csv("data/nodes_keywords.csv")
for _, row in keywords.iterrows():
    kid = str(row['KeywordID'])
    k_node = uri(f"Keyword_{kid}")
    g.add((k_node, RDF.type, EX.Keyword))
    g.add((k_node, RDFS.label, Literal(row['Keyword'])))

rel_about = pd.read_csv("data/rel_about.csv")
for _, row in rel_about.iterrows():
    pid, kid = str(row['PaperID']), str(row['KeywordID'])
    g.add((uri(f"Paper_{pid}"), EX.discusses, uri(f"Keyword_{kid}")))

# === Cites (related) ===
rels = pd.read_csv("data/rel_related.csv")
for _, row in rels.iterrows():
    pid, rid = str(row['PaperID']), str(row['RelatedToPaperID'])
    g.add((uri(f"Paper_{pid}"), EX.cites, uri(f"Paper_{rid}")))

# === Publishers: Conference, Workshop, Journal as Events & PaperCollections ===

def process_pub(node_type, csv_file, id_col, venue_col, year_col):
    df = pd.read_csv(csv_file)
    for _, row in df.iterrows():
        vid = str(row[id_col])
        node = uri(f"{node_type}_{vid}")
        # type both Event and node_type
        g.add((node, RDF.type, EX[node_type]))
        g.add((node, RDF.type, EX.Event))
        # venue
        venue_node = get_venue_node(row[venue_col])
        g.add((node, EX.hasVenue, venue_node))
        # year
        if pd.notna(row[year_col]):
            yr_node = get_year_node(int(row[year_col]))
            g.add((node, EX.hasYear, yr_node))
        return vid, node

# Process each
process_pub('Conference', 'data/nodes_conference.csv', 'ConferenceID', 'Venue', 'Year')
process_pub('Workshop',  'data/nodes_workshop.csv',  'WorkshopID',  'Venue', 'Year')
process_pub('Journal',   'data/nodes_journal.csv',   'JournalID',   'Venue', 'Year')

# === PublisedAt and includes relations ===
# rel_published_in_* links
for csv_file, col, node_type in [
    ("data/rel_published_in_conference.csv", "ConferenceID", "Conference"),
    ("data/rel_published_in_workshop.csv",  "WorkshopID",  "Workshop"),
    ("data/rel_published_in_journal.csv",   "JournalID",   "Journal")
]:
    rel_df = pd.read_csv(csv_file)
    for _, row in rel_df.iterrows():
        pid = str(row['PaperID'])
        vid = str(row[col])
        paper = uri(f"Paper_{pid}")
        coll = uri(f"{node_type}_{vid}")
        # paper published at collection
        g.add((paper, EX.publisedAt, coll))
        # collection includes paper
        g.add((coll, EX.includes, paper))

# === Reviews ===
# Reviewer class and reviews property
reviews = pd.read_csv("data/rel_reviews.csv")
for idx, row in reviews.iterrows():
    rid = str(row['ReviewerID'])
    rev_node = uri(f"Reviewer_{rid}")
    g.add((rev_node, RDF.type, EX.Reviewer))
    # link to paper
    pid = str(row['PaperID'])
    g.add((rev_node, EX.reviews, uri(f"Paper_{pid}")))

# === Serialize ===
abox_path = os.path.join(output_dir, "abox.ttl")
g.serialize(destination=abox_path, format="turtle")
print(f"ABOX saved to {abox_path} with {len(g)} triples.")
