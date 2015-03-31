import sys
import sqlite3
import nltk
import networkx as nx
import config


# dev imports
import random
from pprint import pprint
import matplotlib.pyplot as plt


## DB Functions ##

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



## NLP functions ##

def tag_phrase(phrase):
    taggedlist =  nltk.pos_tag(nltk.word_tokenize(phrase))
    return [( t[0], t[1].lower() ) for t in taggedlist]


## Graph Functions ##


def find_nodeswithtoken(token, G):
    allnodes = G.nodes(data=True)
    toknodes = [n for n in allnodes if n[1]['token'] == token]
    return toknodes


def graph_taggedphrases(phraselist):
    #stopwords = nltk.corpus.stopwords.words('english')
    G = nx.DiGraph()
    newnodeid = 0

    # loop through phrases
    for i, phrase in enumerate(phraselist):
        prevnodeid = None
        phrase.insert(0, ('<S>', 'delim'))
        phrase.append( ('<E>', 'delim') )
        print(' '.join([t[0] for t in phrase]))

        # loop through tokens in phrase
        for j, token in enumerate(phrase):
            wordid = (i, j)
            toknodes = find_nodeswithtoken(token, G)

            # all tokens from 1st phrase in phraselist are added as nodes
            if i == 0:
                G.add_node(newnodeid, token=token, count=1, wordids=[wordid])
                # add edge to previous node, if any
                if prevnodeid is not None:
                    G.add_edge(prevnodeid, newnodeid)
                prevnodeid = newnodeid
                newnodeid += 1

            # if token not found in graph, add node
            elif not toknodes:
                G.add_node(newnodeid, token=token, count=1, wordids=[wordid])
                # add edge to previous node, if any
                if prevnodeid is not None:
                    G.add_edge(prevnodeid, newnodeid)
                prevnodeid = newnodeid
                newnodeid += 1

            # if token is found in graph, assign it to existing node
            else:
                assignednodeid = toknodes[0][0]
                G.node[assignednodeid]['count'] += 1
                G.node[assignednodeid]['wordids'].append(wordid)
                # add edge from previous node, if any, if edge doesn't exist
                if prevnodeid is not None and not G.has_edge(prevnodeid, assignednodeid):
                    G.add_edge(prevnodeid, assignednodeid)
                prevnodeid = assignednodeid
    return G



## Main ##

def main():
    grpids = get_tweetgroupids()
    twtgrp = get_tweetgroup(random.choice(grpids))
    tagphrases = [tag_phrase(twt[4].lower()) for twt in twtgrp]
    G = graph_taggedphrases(tagphrases)
    nodelist = G.nodes(data=True)

    #pprint(nodelist)

    plt.rcParams['figure.figsize'] = [13.5, 8.25]
    pos = nx.spring_layout(G, k=0.3)
    labs = {n[0]: n[1]['token'][0] + '\n' + str(n[1]['count'])  for n in nodelist}
    nx.draw_networkx(G, pos, node_color='w', node_size=1500, labels=labs)
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
