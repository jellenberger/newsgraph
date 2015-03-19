import sys
import sqlite3
import textblob
import config
from textblob import TextBlob

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

def blobify_group(group):
    blobtwts = []
    for twt in group:
        txtblob = TextBlob(twt[4])
        blobtwts.append( (twt[0], twt[1], twt[2], twt[3], txtblob) )
    return blobtwts    



## Main ##

def main():
    grpids = get_tweetgroupids()
    blobgrp = blobify_group(get_tweetgroup(random.choice(grpids)))
    taggrp = [tb[4].tags for tb in blobgrp]
    pprint(taggrp)


if __name__ == "__main__":
    sys.exit(main())
