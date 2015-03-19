import sys
import sqlite3
import nltk
import config


# dev imports
import random
from pprint import pprint


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

def tag_tweetgroup(group):
    taggedtwts = []
    for twt in group:
        taggedtxt = nltk.pos_tag(nltk.word_tokenize(twt[4]))
        taggedtwts.append( (twt[0], twt[1], twt[2], twt[3], taggedtxt) )
    return taggedtwts



## Main ##

def main():
    grpids = get_tweetgroupids()
    taggrp = tag_tweetgroup(get_tweetgroup(random.choice(grpids)))
    pprint(taggrp)


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
