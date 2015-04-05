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



## DB ##

def get_tweetgroupids():
    with sqlite3.connect(config.dbfile) as conn:
        groupids = []
        cursor = conn.cursor()
        # get distinct group ids (could select all since groups is a set)
        cursor.execute(
            '''
            select distinct group_id from tweetgroups
            '''
        )
        for row in cursor.fetchall():
            groupids.append(row[0])
        return groupids


def get_tweetgroup(groupid):
    with sqlite3.connect(config.dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            select * from tweetgroups where group_id = ?
            ''',
            (groupid,)
        )
        group = cursor.fetchall()
        return group



## NLP ##

def tag_phrase(phrase):
    taggedlist =  nltk.pos_tag(nltk.word_tokenize(phrase))
    return [( t[0], t[1] ) for t in taggedlist]



## Graph Building ##

def prev_tokeninphrase(tokenid, phraselist):
    if tokenid[1] == 0:
        return None
    return phraselist[tokenid[0]][tokenid[1] - 1]


def next_tokeninphrase(tokenid, phraselist):
    if tokenid[1] >= len(phraselist[tokenid[0]]):
        return None
    return phraselist[tokenid[0]][tokenid[1] + 1]


def find_nodeswithtoken(token, G):
    matchnodes = [n for n in G.nodes() if G.node[n]['token'] == token]
    return matchnodes


def graph_taggedphrases(phraselist):
    print('')

    stopwords = nltk.corpus.stopwords.words('english')
    punct = string.punctuation
    G = nx.DiGraph()
    newnodeid = 0

    # loop through phrases
    for i, phrase in enumerate(phraselist):
        prevnodeid = None
        assignednodes = set()
        phrase.insert(0, ('START', 'DELIM'))
        phrase.append( ('END', 'DELIM') )

        print(' '.join([t[0] + '/' + t[1] for t in phrase]))

        # loop through tokens in phrase
        for j, token in enumerate(phrase):
            # variables used by graph population code
            tokenid = (i, j)
            isfirstphrase = (i == 0)
            isstopword = token[0] in stopwords
            ispunct = token[0] in punct
            isfrag = token[0].startswith("'") # 's or contraction verb
            matchnodes = set(find_nodeswithtoken(token, G))
            candidatenodes = list(matchnodes - assignednodes)
            ncandidates = len(candidatenodes)

            # token is in first phrase or has no matching nodes, add node to G
            #if nmatches == 0 or isfirstphrase:
            if ncandidates == 0 or isfirstphrase:
                # add node for token
                G.add_node(newnodeid, token=token, count=1, tokenids=[tokenid])
                # add edge to previous node, if any
                if prevnodeid is not None:
                    G.add_edge(prevnodeid, newnodeid)
                assignednodes.add(newnodeid)
                prevnodeid = newnodeid
                newnodeid += 1

            # token has only 1 matching node and is a non-stopword
            elif ncandidates == 1 and not (isstopword or ispunct or isfrag):
                # assign token to only matched node
                assignednode = candidatenodes[0]
                G.node[assignednode]['count'] += 1
                G.node[assignednode]['tokenids'].append(tokenid)
                # add edge from previous node, if there is one, if edge doesn't exist
                if prevnodeid is not None and not G.has_edge(prevnodeid, assignednode):
                    G.add_edge(prevnodeid, assignednode)
                assignednodes.add(assignednode)
                prevnodeid = assignednode

            # token has > 1 matching node and is a non-stopword
            elif not (isstopword or ispunct or isfrag):
                pass

            # token is a stopword
            else:
                adjtoks = [prev_tokeninphrase(tokenid, phraselist),
                           next_tokeninphrase(tokenid, phraselist)]
                mnodescontext = []
                for n in candidatenodes:
                    predtoks = [G.node[pnode]['token'] for pnode in G.predecessors(n)]
                    succtoks = [G.node[pnode]['token'] for pnode in G.successors(n)]
                    nmatchcontext = len(set(predtoks + succtoks) & set(adjtoks))
                    mnodescontext.append(nmatchcontext)
                bestcontext = max(mnodescontext)
                if bestcontext > 0:
                    bestcontextnode = candidatenodes[mnodescontext.index(bestcontext)]
                else:
                    bestcontextnode = None
                if bestcontextnode is not None:
                    assignednode = bestcontextnode
                    G.node[assignednode]['count'] += 1
                    G.node[assignednode]['tokenids'].append(tokenid)
                    # add edge from previous node, if there is one, if edge doesn't exist
                    if prevnodeid is not None and not G.has_edge(prevnodeid, assignednode):
                        G.add_edge(prevnodeid, assignednode)
                    assignednodes.add(assignednode)
                    prevnodeid = assignednode
                else:
                    # add node for token
                    G.add_node(newnodeid, token=token, count=1, tokenids=[tokenid])
                    # add edge to previous node, if any
                    if prevnodeid is not None:
                        G.add_edge(prevnodeid, newnodeid)
                    assignednodes.add(newnodeid)
                    prevnodeid = newnodeid
                    newnodeid += 1
    return G



## Main ##

def main():
    grpids = get_tweetgroupids()
    twtgrp = get_tweetgroup(random.choice(grpids))
    tagphrases = [tag_phrase(twt[4].lower()) for twt in twtgrp]
    G = graph_taggedphrases(tagphrases)
    nodelist = G.nodes(data=True)

    #pprint(nodelist)

    plt.rcParams['figure.figsize'] = [14.0, 8.3]
    pos = nx.spring_layout(G, k=0.3)
    labs = {n[0]: n[1]['token'][0] + '\n' + str(n[1]['count'])  for n in nodelist}
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
