import sys
import random
import pickle
import networkx as nx
import grapher
from nltk.util import ngrams
import math


## Weighting ##

def get_weightedpaths(G):
    startnode = grapher.find_nodeswithtoken(('START', 'START'), G)[0]
    endnode = grapher.find_nodeswithtoken(('END', 'END'), G)[0]
    nodepaths = nx.all_simple_paths(G, startnode, endnode)
    weightedpaths = []
    for nodelist in nodepaths:
        edges = list(zip(nodelist, nodelist[1:]))
        numedges = len(edges)
        pathweight = sum([G.edge[u][v]['weight'] for u, v in edges])
        pathtokens = [G.node[n]['token'] for n in nodelist]
        weightedpaths.append((pathtokens, pathweight, numedges))
    return weightedpaths


## Main ##

def main():
    print('')

    verbtags = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}

    with open('../data/4grammodel.pickle', 'rb') as f:
        g_model = pickle.load(f)

    grpids = grapher.get_tweetgroupids()
    twtgrp = grapher.get_tweetgroup(random.choice(grpids))
    taggedphrases = [grapher.tag_phrase(twt[4].lower()) for twt in twtgrp]
    G = grapher.graph_taggedphrases(taggedphrases)
    G = grapher.weight_edges(G)
    paths = get_weightedpaths(G)
    #verbed_paths = list(filter(lambda path: any([t[1] in verbtags for t in path[0]]), paths))
    sorted_paths = sorted(paths[:30], key=lambda x: (x[1], x[2]))
    resorted_paths = sorted(sorted_paths, key=lambda x: (x[1]/x[2], x[2]))

    for phrase in taggedphrases:
        print(' '.join([word[0] for word in phrase]))
    print('')

    for path in sorted_paths[:2]:
        print(' '.join([tok[0] for tok in path[0]]))
    print('')

    for path in resorted_paths[:2]:
        print(' '.join([tok[0] for tok in path[0]]))
    print('')

    for path in sorted_paths[:10]:
        words = [tok[0] for tok in path[0]]
        del words[0]
        del words[-1]
        pos_tags = [tok[1] for tok in path[0]]
        del pos_tags[0]
        del pos_tags[-1]
        tag_ngrams = list(ngrams(pos_tags, 4))
        g_model_score = math.log(sum([g_model[ngram] for ngram in tag_ngrams]) / len(tag_ngrams))
        phrase = ' '.join(words)
        print(g_model_score, ' ', phrase)


if __name__ == "__main__":
    sys.exit(main())


## Notes ##

'''
'''
