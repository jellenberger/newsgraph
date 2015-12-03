# Notes for Pisgah #

## Tweet Processing ##
- decrease cleanup modifications
- what to do with urls and hastags?

## Grouping
- eliminate duplicates within match group
- process chronologically (look for groups in newer material)
- duplicate detection doesn't seem to be working - is it applied after cleanup?
- detect duplicate word roots and eliminate?

## Graphing
- require punct, possessives and contraction verbs to follow same word?
- save graph objects to db
- move to pydot

## Weighting and Ranking
- use edge count in weighting?
- determine how, when  to normalize weighting for paths from start and end

## Grammaticality
- n-gram models should include beginning and end