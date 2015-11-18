import sys
import random
import networkx as nx
import grapher


## Weighting ##

def get_weightedpaths(G):
    startnode = grapher.find_nodeswithtoken(('START', 'DELIM'), G)[0]
    endnode = grapher.find_nodeswithtoken(('END', 'DELIM'), G)[0]
    nodepaths = nx.all_simple_paths(G, startnode, endnode)
    weightedpaths = []
    for nodelist in nodepaths:
        edges = list(zip(nodelist, nodelist[1:]))
        numedges = len(edges)
        pathweight = sum([G.edge[u][v]['weight'] for u, v in edges])
        pathphrase = [G.node[n]['token'][0] for n in nodelist]
        weightedpaths.append((pathphrase, pathweight, numedges))
    return weightedpaths


## Main ##

def main():
    print('')

    grpids = grapher.get_tweetgroupids()
    twtgrp = grapher.get_tweetgroup(random.choice(grpids))
    taggedphrases = [grapher.tag_phrase(twt[4].lower()) for twt in twtgrp]
    G = grapher.graph_taggedphrases(taggedphrases)
    G = grapher.weight_edges(G)
    weightedpaths = get_weightedpaths(G)
    sortedpaths = sorted(weightedpaths, key=lambda x: (x[1], x[2]))
    resortedpaths = sorted(sortedpaths[:10], key=lambda x: (x[1]/x[2], x[2]))

    for phrase in taggedphrases:
        print(' '.join([w[0] for w in phrase]))
    print('')

    for path in resortedpaths:
        print(' '.join(path[0]))
    print('')


if __name__ == "__main__":
    sys.exit(main())


## Notes ##

'''
'''
