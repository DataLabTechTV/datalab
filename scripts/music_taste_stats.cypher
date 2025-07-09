MATCH (u:User)
RETURN 1 AS index, "No. User Nodes" AS stat, count(*) AS val

UNION

MATCH (g:Genre)
RETURN 2 AS index, "No. Genre Nodes" AS stat, count(*) AS val

UNION

MATCH (t:Track)
RETURN 3 AS index, "No. Track Nodes" AS stat, count(*) AS val

UNION

MATCH (n)
RETURN 4 AS index, "Total No. Nodes" AS stat, count(*) AS val

UNION

MATCH ()-[:Friend]->()
RETURN 5 AS index, "No. Friend Rels" AS stat, count(*) AS val

UNION

MATCH ()-[:Likes]->()
RETURN 6 AS index, "No. Likes Rels" AS stat, count(*) AS val

UNION

MATCH ()-[:ListenedTo]->()
RETURN 7 AS index, "No. ListenedTo Rels" AS stat, count(*) AS val

UNION

MATCH ()-[:Tagged]->()
RETURN 8 AS index, "No. Tagged Rels" AS stat, count(*) AS val

UNION

MATCH ()-[]->()
RETURN 9 AS index, "Total No. Rels" AS stat, count(*) AS val;
