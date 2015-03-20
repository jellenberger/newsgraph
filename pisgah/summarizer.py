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
    return nltk.pos_tag(nltk.word_tokenize(phrase))



## Graph Functions ##

def graph_taggedphrases(phraselist):
    G = nx.DiGraph()
    nodeidx = 0
    for phrase in phraselist[:1]:
        phrase.insert(0, ('<START>', 'START'))
        phrase.append( ('<END>', 'END') )
        prevnode = None
        for token in phrase:
            node = (token[0].lower(), token[1].lower)
            G.add_node(node)
            if prevnode:
                G.add_edge(prevnode, node)
            prevnode = node
            nodeidx += 1
    return G



## Main ##

def main():
    grpids = get_tweetgroupids()
    twtgrp = get_tweetgroup(random.choice(grpids))
    tagphrases = [tag_phrase(twt[4]) for twt in twtgrp]
    plt.rcParams['figure.figsize'] = [11.0, 8.5]
    G = graph_taggedphrases(tagphrases)
    pos = nx.circular_layout(G)
    labs = {n: n[0] for n in nx.nodes(G)}
    nx.draw_networkx(G, pos, node_color='w', node_size=1500, labels=labs)
    plt.axis('off')
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
