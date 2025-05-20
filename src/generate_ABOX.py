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

def uri(local: str) -> URIRef:
    return EX[local]

# === Caches for re‐use ===
_year_nodes = {}
_venue_nodes = {}
_abstract_nodes = {}

def get_year_node(year: int) -> URIRef:
    key = f"Year_{year}"
    if key not in _year_nodes:
        node = uri(key)
        g.add((node, RDF.type, EX.Year))
        g.add((node, RDFS.label, Literal(year, datatype=None)))
        _year_nodes[key] = node
    return _year_nodes[key]

def get_venue_node(name: str) -> URIRef:
    key = f"Venue_{name.replace(' ', '_')}"
    if key not in _venue_nodes:
        node = uri(key)
        g.add((node, RDF.type, EX.Venue))
        g.add((node, RDFS.label, Literal(name)))
        _venue_nodes[key] = node
    return _venue_nodes[key]

def get_abstract_node(pid: str, text: str) -> URIRef:
    key = f"Abstract_{pid}"
    if key not in _abstract_nodes:
        node = uri(key)
        g.add((node, RDF.type, EX.Abstract))
        g.add((node, RDFS.label, Literal(text)))
        _abstract_nodes[key] = node
    return _abstract_nodes[key]

# === Load Papers from nodes_papers.csv ===
papers_df = pd.read_csv("data/nodes_papers.csv")
for _, row in papers_df.iterrows():
    pid = str(row['PaperID'])
    paper_node = uri(f"Paper_{pid}")
    g.add((paper_node, RDF.type, EX.Paper))
    # Title → rdfs:label
    if pd.notna(row['Title']):
        g.add((paper_node, RDFS.label, Literal(row['Title'])))
    # Year → ex:hasYear
    if pd.notna(row['Year']):
        yr_node = get_year_node(int(row['Year']))
        g.add((paper_node, EX.hasYear, yr_node))
    # DOI (optional)
    if 'DOI' in row and pd.notna(row['DOI']):
        g.add((paper_node, EX.hasDOI, Literal(row['DOI'])))
    # Abstract → ex:summarizedBy
    if pd.notna(row['Abstract']):
        abs_node = get_abstract_node(pid, row['Abstract'])
        g.add((paper_node, EX.summarizedBy, abs_node))

# === Load Authors and author-paper relations ===
authors = pd.read_csv("data/nodes_authors.csv")
for _, row in authors.iterrows():
    aid = str(row['AuthorID'])
    author_node = uri(f"Author_{aid}")
    g.add((author_node, RDF.type, EX.Author))
    if pd.notna(row['Name']):
        g.add((author_node, RDFS.label, Literal(row['Name'])))
    if pd.notna(row['Affiliation']):
        g.add((author_node, EX.affiliation, Literal(row['Affiliation'])))

rel_auth = pd.read_csv("data/rel_author_of.csv")
for _, row in rel_auth.iterrows():
    aid, pid = str(row['AuthorID']), str(row['PaperID'])
    g.add((uri(f"Author_{aid}"), EX.writes, uri(f"Paper_{pid}")))

# === Corresponding authors ===
rel_corr = pd.read_csv("data/rel_corresponding_author.csv")
for _, row in rel_corr.iterrows():
    aid, pid = str(row['AuthorID']), str(row['PaperID'])
    inst = uri(f"CorrAuth_{aid}_{pid}")
    g.add((inst, RDF.type, EX.IsCorrespondingAuthorOf))
    g.add((inst, EX.writes, uri(f"Paper_{pid}")))
    # also ensure the Author→Paper link exists
    g.add((uri(f"Author_{aid}"), EX.writes, uri(f"Paper_{pid}")))

# === Keywords and discusses ===
keywords = pd.read_csv("data/nodes_keywords.csv")
for _, row in keywords.iterrows():
    kid = str(row['KeywordID'])
    kn = uri(f"Keyword_{kid}")
    g.add((kn, RDF.type, EX.Keyword))
    g.add((kn, RDFS.label, Literal(row['Keyword'])))

rel_about = pd.read_csv("data/rel_about.csv")
for _, row in rel_about.iterrows():
    pid, kid = str(row['PaperID']), str(row['KeywordID'])
    g.add((uri(f"Paper_{pid}"), EX.discusses, uri(f"Keyword_{kid}")))

# === Citations (related) ===
rels = pd.read_csv("data/rel_related.csv")
for _, row in rels.iterrows():
    pid, rid = str(row['PaperID']), str(row['RelatedToPaperID'])
    g.add((uri(f"Paper_{pid}"), EX.cites, uri(f"Paper_{rid}")))

# === Conferences, Workshops, Journals as Events & Collections ===
def process_pub(node_type, csv_file, id_col, venue_col, year_col):
    df = pd.read_csv(csv_file)
    for _, row in df.iterrows():
        vid = str(row[id_col])
        node = uri(f"{node_type}_{vid}")
        g.add((node, RDF.type, EX[node_type]))
        g.add((node, RDF.type, EX.Event))
        # Venue
        vn = get_venue_node(row[venue_col])
        g.add((node, EX.hasVenue, vn))
        # Year
        if pd.notna(row[year_col]):
            yn = get_year_node(int(row[year_col]))
            g.add((node, EX.hasYear, yn))

process_pub('Conference', 'data/nodes_conference.csv', 'ConferenceID', 'Venue', 'Year')
process_pub('Workshop',  'data/nodes_workshop.csv',  'WorkshopID',   'Venue', 'Year')
process_pub('Journal',   'data/nodes_journal.csv',   'JournalID',    'Venue', 'Year')

# === Publication links ===
for csv_file, col, node_type in [
    ("data/rel_published_in_conference.csv", "ConferenceID", "Conference"),
    ("data/rel_published_in_workshop.csv",  "WorkshopID",   "Workshop"),
    ("data/rel_published_in_journal.csv",   "JournalID",    "Journal")
]:
    rel_df = pd.read_csv(csv_file)
    for _, row in rel_df.iterrows():
        pid, vid = str(row['PaperID']), str(row[col])
        paper = uri(f"Paper_{pid}")
        coll  = uri(f"{node_type}_{vid}")
        g.add((paper, EX.publisedAt, coll))
        g.add((coll, EX.includes, paper))

# === Reviews ===
reviews = pd.read_csv("data/rel_reviews.csv")
for _, row in reviews.iterrows():
    rid = str(row['ReviewerID'])
    rnode = uri(f"Reviewer_{rid}")
    g.add((rnode, RDF.type, EX.Reviewer))
    pid = str(row['PaperID'])
    g.add((rnode, EX.reviews, uri(f"Paper_{pid}")))
    if pd.notna(row['Comment']):
        g.add((rnode, EX.reviewComment, Literal(row['Comment'])))
    if pd.notna(row['Score']):
        g.add((rnode, EX.reviewScore, Literal(row['Score'])))

# === Serialize ABox ===
abox_path = os.path.join(output_dir, "abox.ttl")
g.serialize(destination=abox_path, format="turtle")
print(f"ABOX saved to {abox_path} with {len(g)} triples.")
