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
