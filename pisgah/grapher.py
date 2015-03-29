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


def get_nodeswithtoken(token, G):
    allnodes = G.nodes(data=True)
    toknodes = [n[0] for n in allnodes if n[1]['token'] == token]
    return toknodes


def graph_taggedphrases(phraselist):
    #stopwords = nltk.corpus.stopwords.words('english')
    G = nx.DiGraph()
    newnodeid = 0
    for phrase in phraselist:
        prevnodeid = None
        phrase.insert(0, ('START', 'delim'))
        phrase.append( ('END', 'delim') )
        print(' '.join([t[0] for t in phrase]))
        for token in phrase:
            toknodes = get_nodeswithtoken(token, G)
            if not toknodes:
                G.add_node(newnodeid, token=token, count=1)
                if prevnodeid is not None:
                    G.add_edge(prevnodeid, newnodeid)
                prevnodeid = newnodeid
                newnodeid += 1
            else:
                assignednodeid = toknodes[0]
                G.node[assignednodeid]['count'] += 1
                if prevnodeid is not None and not G.has_edge(prevnodeid, assignednodeid):
                    G.add_edge(prevnodeid, assignednodeid)
                prevnodeid = assignednodeid
    return G



## Main ##

def main():
    plt.rcParams['figure.figsize'] = [14.0, 8.5]
    grpids = get_tweetgroupids()
    twtgrp = get_tweetgroup(random.choice(grpids))
    tagphrases = [tag_phrase(twt[4].lower()) for twt in twtgrp]
    G = graph_taggedphrases(tagphrases)
    pos = nx.spring_layout(G, k=0.4)
    nodelist = G.nodes(data=True)
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
