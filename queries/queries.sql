# Test Query: Show first 10 papers and their titles
SELECT ?paper ?title
WHERE {
  ?paper a <http://example.org/Paper> ;
         <http://example.org/hasTitle> ?title .
}
LIMIT 10

# Insightful Query: Authors with multiple papers
SELECT ?author (COUNT(?paper) AS ?paperCount)
WHERE {
  ?author a <http://example.org/Author> ;
          <http://example.org/authorOf> ?paper .
}
GROUP BY ?author
HAVING (COUNT(?paper) > 1)
ORDER BY DESC(?paperCount)


-- What is the growth of papers and authors by venue and year discussing a topic ‘X’?


PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ex: <http://example.org/schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?collectionType ?collection_name ?year (COUNT(?paper) AS ?paperCount) (COUNT(?author) AS ?authorCount)
WHERE {
  ?collection rdf:type ?collectionType .
  ?collection ex:hasYear ?year .
  ?collection ex:includes ?paper .
  ?author ex:writes ?paper .
  ?paper ex:discusses ?keyword .
  ?keyword rdfs:label "data processing" .
  ?collection rdfs:label ?collection_name . 
  FILTER(?collectionType IN (ex:Workshop, ex:Conference, ex:Journal))
}
GROUP BY ?collectionType ?collection_name ?year
ORDER BY ASC(?collection_name) DESC(?year)