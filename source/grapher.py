import sys
import sqlite3
import nltk
import networkx as nx
import config
import string


import random
import matplotlib.pyplot as plt


## Classes ##

class WordGraph(nx.DiGraph):
    def __init__(self):
        nx.DiGraph.__init__(self)
        self.newnodeid = 0
        self.prevnodeid = None
        self.assignednodes = []

    def add_wordnode(self, token, tokenid):
        nodeid = self.newnodeid
        self.add_node(nodeid, token=token, count=1, tokenids=[tokenid])
        # add edge to previous node, if any
        if self.prevnodeid is not None:
            self.add_edge(self.prevnodeid, nodeid, count=1, weight=0)
        self.assignednodes.append(nodeid)
        self.prevnodeid = nodeid
        self.newnodeid += 1
        return nodeid

    def assign_wordnode(self, nodeid, tokenid):
        self.node[nodeid]['count'] += 1
        self.node[nodeid]['tokenids'].append(tokenid)
        # add edge from previous node, if any, where edge doesn't exist
        if self.prevnodeid is not None:
            if self.has_edge(self.prevnodeid, nodeid):
                self.edge[self.prevnodeid][nodeid]['count'] += 1
            else:
                self.add_edge(self.prevnodeid, nodeid, count=1, weight=0)              
        self.assignednodes.append(nodeid)
        self.prevnodeid = nodeid
        return nodeid

    def start_newphrase(self):
        self.prevnodeid = None
        self.assignednodes = []


## DB ##

def get_tweetgroupids():
    with sqlite3.connect(config.dbfile) as conn:
        groupids = []
        cursor = conn.cursor()
        # get distinct group ids (could select all since groups is a set)
        cursor.execute('select distinct group_id from tweetgroups')
        for row in cursor.fetchall():
            groupids.append(row[0])
        return groupids


def get_tweetgroup(groupid):
    with sqlite3.connect(config.dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute('select * from tweetgroups where group_id = ?',
                       (groupid, ))
        group = cursor.fetchall()
        return group


## NLP ##

def tag_phrase(phrase):
    taggedlist = nltk.pos_tag(nltk.word_tokenize(phrase))
    return [(t[0], t[1]) for t in taggedlist]



## Graph Utils ##

def prev_token(tokenid, phraselist):
    if tokenid[1] == 0:
        return None
    return phraselist[tokenid[0]][tokenid[1] - 1]


def next_token(tokenid, phraselist):
    if tokenid[1] >= len(phraselist[tokenid[0]]):
        return None
    return phraselist[tokenid[0]][tokenid[1] + 1]


def find_nodeswithtoken(token, G):
    matchnodes = [n for n in G.nodes_iter() if G.node[n]['token'] == token]
    return matchnodes


def find_contextcandidate(tokenid, phraselist, candidatenodes, G):
    adjtoks = [prev_token(tokenid, phraselist),
               next_token(tokenid, phraselist)]
    contextcounts = []
    for n in candidatenodes:
        predtoks = [G.node[pnode]['token'] for pnode in G.predecessors(n)]
        succtoks = [G.node[pnode]['token'] for pnode in G.successors(n)]
        contextcount = len(set(predtoks + succtoks) & set(adjtoks))
        contextcounts.append(contextcount)
    bestcount = max(contextcounts)
    if bestcount > 0:
        return candidatenodes[contextcounts.index(bestcount)]
    else:
        return None


def find_countcandidate(candidatenodes, G):
    counts = [G.node[n]['count'] for n in candidatenodes]
    bestcount = candidatenodes[counts.index(max(counts))]
    return bestcount


## Graphing ##

def graph_taggedphrases(phraselist):

    stopwords = nltk.corpus.stopwords.words('english')
    punct = string.punctuation
    G = WordGraph()

    # loop through phrases
    for i, phrase in enumerate(phraselist):
        G.start_newphrase()
        isfirstphrase = (i == 0)
        phrase.insert(0, ('START', 'DELIM'))
        phrase.append(('END', 'DELIM'))

        print(' '.join([t[0] for t in phrase]))

        # loop through tokens in phrase
        for j, token in enumerate(phrase):
            # variables used by graph population code
            tokenid = (i, j)
            isstopword = token[0] in stopwords
            ispunct = token[0] in punct
            isfrag = token[0].startswith("'") # 's or contraction verb
            matchnodes = find_nodeswithtoken(token, G)
            candidatenodes = list(set(matchnodes) -
                                  set(G.assignednodes))
            ncandidates = len(candidatenodes)

            # if first phrase, add new node for token
            if isfirstphrase:
                G.add_wordnode(token, tokenid)

            # if non-stopword
            elif not (isstopword or ispunct or isfrag):

                # if no matching nodes, add node for token
                if ncandidates == 0:
                    G.add_wordnode(token, tokenid)

                # if only 1 matching node, assign token to it
                elif ncandidates == 1:
                    assignednode = candidatenodes[0]
                    G.assign_wordnode(assignednode, tokenid)

                # if > 1 matching node, pick best node for assignment
                else:
                    bestcontextnode = find_contextcandidate(tokenid, phraselist,
                                                            candidatenodes, G)
                    bestcountnode = find_countcandidate(candidatenodes, G)
                    if bestcontextnode is not None:
                        G.assign_wordnode(bestcontextnode, tokenid)
                    else:
                        G.add_wordnode(token, tokenid)

            # if a stopword
            else:

                # if no matching node, add node for token
                if ncandidates == 0:
                    G.add_wordnode(token, tokenid)

                # if >= 1 matching nodes, pick best node
                else:
                    bestcontextnode = find_contextcandidate(tokenid, phraselist, 
                                                            candidatenodes, G)
                    if bestcontextnode is not None:
                        G.assign_wordnode(bestcontextnode, tokenid)
                    else:
                        G.add_wordnode(token, tokenid)

    return G

def weight_edges(G):
    for u, v in G.edges():
        countu = G.node[u]['count']
        countv = G.node[v]['count']
        #edgecount = G.edge[u][v]['count']
        distsum = 0
        for su, i in G.node[u]['tokenids']:
            for sv, j in G.node[v]['tokenids']:
                if su == sv and j > i:
                    distsum += (j - i)
        #w = (countu + countv) / (edgecount / distsum)
        w = (countu + countv) / (1 / distsum)
        wprime = w / (countv * countu)
        G.edge[u][v]['weight'] = wprime
    return G


## Main ##

def main():

    grpids = get_tweetgroupids()
    twtgrp = get_tweetgroup(random.choice(grpids))
    tagphrases = [tag_phrase(twt[4].lower()) for twt in twtgrp]
    G = graph_taggedphrases(tagphrases)
    G = weight_edges(G)
    nodelist = G.nodes(data=True)
    edgelist = G.edges(data=True)

    print('')

    '''
    from pprint import pprint
    pprint(G.edges(data=True))
    '''

    plt.rcParams['figure.figsize'] = [16.0, 12.0]
    pos = nx.spring_layout(G, k=0.3)
    nlabs = {n[0]: n[1]['token'][0] + '\n' + 
             str(n[1]['count'])
             for n in nodelist}
    elabs = {(e[0], e[1]): str(round(e[2]['weight'], 2)) for e in edgelist}
    nx.draw_networkx(G, pos, node_color='w', node_size=1250, labels=nlabs)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=elabs)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    sys.exit(main())


## Notes ##

'''
models punkt
corpora stopwords
maxent_treebank_pos_tagger

nltk.data.path

STOP_TYPES = ['DET', 'CNJ']
text = """some data here"""
tokens = nltk.pos_tag(nltk.word_tokenize(text))
good_words = [w for w, wtype in token if wtype not in STOP_TYPES]

'''
