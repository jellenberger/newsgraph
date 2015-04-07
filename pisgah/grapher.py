import sys
import sqlite3
import nltk
import networkx as nx
import config
import string

# dev imports
import random
from pprint import pprint
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
            self.add_edge(self.prevnodeid, nodeid)
        self.assignednodes.append(nodeid)
        self.prevnodeid = nodeid
        self.newnodeid += 1
        return nodeid
 
    def assign_wordnode(self, nodeid, tokenid):
        self.node[nodeid]['count'] += 1
        self.node[nodeid]['tokenids'].append(tokenid)
        # add edge from previous node, if any, where edge doesn't exist
        if (self.prevnodeid is not None and not
            self.has_edge(self.prevnodeid, nodeid)):
            self.add_edge(self.prevnodeid, nodeid)
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
    taggedlist =  nltk.pos_tag(nltk.word_tokenize(phrase))
    return [( t[0], t[1] ) for t in taggedlist]



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
    matchnodes = [n for n in G.nodes() if G.node[n]['token'] == token]
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
    print('')

    stopwords = nltk.corpus.stopwords.words('english')
    punct = string.punctuation
    G = WordGraph()

    # loop through phrases
    for i, phrase in enumerate(phraselist):
        G.start_newphrase()
        phrase.insert(0, ('START', 'DELIM'))
        phrase.append( ('END', 'DELIM') )

        print(' '.join([t[0] for t in phrase]))

        # loop through tokens in phrase
        for j, token in enumerate(phrase):
            # variables used by graph population code
            tokenid = (i, j)
            isfirstphrase = (i == 0)
            isstopword = token[0] in stopwords
            ispunct = token[0] in punct
            isfrag = token[0].startswith("'") # 's or contraction verb
            matchnodes = find_nodeswithtoken(token, G)
            candidatenodes = list(set(matchnodes) - set(G.assignednodes)) #TODO check that this is working
            ncandidates = len(candidatenodes)

            # if token in first phrase or has no matching nodes, add node to G
            #if nmatches == 0 or isfirstphrase:
            if ncandidates == 0 or isfirstphrase:
                G.add_wordnode(token, tokenid)

            # token has only 1 matching node and is a non-stopword
            elif ncandidates == 1 and not (isstopword or ispunct or isfrag):
                # assign token to only matched node
                assignednode = candidatenodes[0]
                G.assign_wordnode(assignednode, tokenid)

            # token has > 1 matching node and is a non-stopword
            elif not (isstopword or ispunct or isfrag):
                bestcontextnode = find_contextcandidate(tokenid, phraselist, candidatenodes, G)
                bestcountnode = find_countcandidate(candidatenodes, G) #TODO Check that this is working
                if bestcontextnode is not None:
                    G.assign_wordnode(bestcontextnode, tokenid)
                else:
                    G.add_wordnode(token, tokenid)

            # token is a stopword
            elif isstopword or ispunct or isfrag:
                bestcontextnode = find_contextcandidate(tokenid, phraselist, candidatenodes, G)
                if bestcontextnode is not None:
                    G.assign_wordnode(bestcontextnode, tokenid)
                else:
                    G.add_wordnode(token, tokenid)

            else:
                print('Unmapped word.')

    return G



## Main ##

def main():
    grpids = get_tweetgroupids()
    twtgrp = get_tweetgroup(random.choice(grpids))
    tagphrases = [tag_phrase(twt[4].lower()) for twt in twtgrp]
    G = graph_taggedphrases(tagphrases)
    nodelist = G.nodes(data=True)

    plt.rcParams['figure.figsize'] = [14.0, 8.3]
    pos = nx.spring_layout(G, k=0.3)
    labs = {n[0]: n[1]['token'][0] + '\n' + str(n[1]['count'])  
            for n in nodelist}
    nx.draw_networkx(G, pos, node_color='w', node_size=1800, labels=labs)
    #plt.axis('off')
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
