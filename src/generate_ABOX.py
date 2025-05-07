import pandas as pd
from rdflib import Graph, Namespace, RDF, Literal
import os

# === Setup ===
g = Graph()
EX = Namespace("http://example.org/")
g.bind("ex", EX)

def uri(id_str):
    return EX[str(id_str).strip()]

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# === Authors ===
authors = pd.read_csv("data/nodes_authors.csv")
for _, row in authors.iterrows():
    a = uri(row["AuthorID"])
    g.add((a, RDF.type, EX.Author))
    g.add((a, EX.fullName, Literal(row["Name"])))
    g.add((a, EX.affiliatedTo, Literal(row["Affiliation"])))

# === Papers ===
papers = pd.read_csv("data/nodes_papers.csv")
for _, row in papers.iterrows():
    p = uri(row["PaperID"])
    g.add((p, RDF.type, EX.Paper))
    g.add((p, EX.hasTitle, Literal(row["Title"])))
    g.add((p, EX.hasYear, Literal(int(row["Year"]))))
    g.add((p, EX.hasAbstract, Literal(row["Abstract"])))
    g.add((p, EX.hasDOI, Literal(row["DOI"])))

# === Keywords ===
keywords = pd.read_csv("data/nodes_keywords.csv")
for _, row in keywords.iterrows():
    k = uri(row["KeywordID"])
    g.add((k, RDF.type, EX.Keyword))
    g.add((k, EX.keywordName, Literal(row["Keyword"])))

# === Conferences ===
conf = pd.read_csv("data/nodes_conference.csv")
for _, row in conf.iterrows():
    c = uri(row["ConferenceID"])
    g.add((c, RDF.type, EX.Conference))
    g.add((c, EX.hasTitle, Literal(row["Venue"])))
    g.add((c, EX.hasYear, Literal(int(row["Year"]))))

# === Workshops ===
workshops = pd.read_csv("data/nodes_workshop.csv")
for _, row in workshops.iterrows():
    w = uri(row["WorkshopID"])
    g.add((w, RDF.type, EX.Workshop))
    g.add((w, EX.hasTitle, Literal(row["Venue"])))
    g.add((w, EX.hasYear, Literal(int(row["Year"]))))

# === Journals ===
journals = pd.read_csv("data/nodes_journal.csv")
for _, row in journals.iterrows():
    j = uri(row["JournalID"])
    g.add((j, RDF.type, EX.Journal))
    g.add((j, EX.hasTitle, Literal(row["Venue"])))
    g.add((j, EX.hasYear, Literal(int(row["Year"]))))
    g.add((j, EX.hasVolume, Literal(int(row["Volume"]))))

# === Reviews ===
reviews = pd.read_csv("data/rel_reviews.csv")
for idx, row in reviews.iterrows():
    r = uri(f"review_{idx}")
    g.add((r, RDF.type, EX.Review))
    g.add((r, EX.reviews, uri(row["PaperID"])))
    g.add((uri(row["ReviewerID"]), EX.wroteReview, r))
    g.add((r, EX.reviewComment, Literal(row["Comment"])))
    g.add((r, EX.reviewScore, Literal(int(row["Score"]))))

# === RELATIONSHIPS ===

# authorOf
rel = pd.read_csv("data/rel_author_of.csv")
for _, row in rel.iterrows():
    g.add((uri(row["AuthorID"]), EX.authorOf, uri(row["PaperID"])))

# correspondingAuthor
rel = pd.read_csv("data/rel_corresponding_author.csv")
for _, row in rel.iterrows():
    g.add((uri(row["AuthorID"]), EX.correspondingAuthor, uri(row["PaperID"])))

# about (Paper → Keyword)
rel = pd.read_csv("data/rel_about.csv")
for _, row in rel.iterrows():
    g.add((uri(row["PaperID"]), EX.about, uri(row["KeywordID"])))

# related (Paper → Paper)
rel = pd.read_csv("data/rel_related.csv")
for _, row in rel.iterrows():
    g.add((uri(row["PaperID"]), EX.related, uri(row["RelatedToPaperID"])))

# publishedInConference
rel = pd.read_csv("data/rel_published_in_conference.csv")
for _, row in rel.iterrows():
    g.add((uri(row["PaperID"]), EX.publishedInConference, uri(row["ConferenceID"])))

# publishedInWorkshop
rel = pd.read_csv("data/rel_published_in_workshop.csv")
for _, row in rel.iterrows():
    g.add((uri(row["PaperID"]), EX.publishedInWorkshop, uri(row["WorkshopID"])))

# publishedInJournal
rel = pd.read_csv("data/rel_published_in_journal.csv")
for _, row in rel.iterrows():
    g.add((uri(row["PaperID"]), EX.publishedInJournal, uri(row["JournalID"])))

# === Serialize ABOX ===
abox_path = os.path.join(output_dir, "abox.ttl")
g.serialize(destination=abox_path, format="turtle")
print(f"ABOX saved to {abox_path} with {len(g)} triples.")
