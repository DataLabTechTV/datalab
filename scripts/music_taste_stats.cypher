MATCH (n)
RETURN "No. " + label(n) + " Nodes" AS stat, count(*) AS val

UNION

MATCH (n)
RETURN "Total No. Nodes" AS stat, count(*) AS val

UNION

MATCH ()-[r]->()
RETURN "No. " + label(r) + " Rels" AS stat, count(*) AS val

UNION

MATCH ()-[]->()
RETURN "Total No. Rels" AS stat, count(*) AS val;
