import sys
import re
import uuid
import sqlite3
from textblob import TextBlob
from fuzzywuzzy import fuzz
import config
import textutils as tu

# dev imports
import random
from pprint import pprint



def cleantweettext(twttext):
    twttext = tu.asciichars(twttext)
    twttext = tu.normspace(twttext)
    twttext = tu.unescape(twttext)
    twttext = tu.rmurls(twttext)
    twttext = tu.puncspace(twttext)
    twttext = twttext.replace('#', '')
    twttext = twttext.replace('@', '')
    twttext = tu.singlespaces(twttext).strip()
    return twttext


def retrievetweets():
    with sqlite3.connect(config.dbfile) as conn:
        tweetlist = []
        cursor = conn.cursor()
        cursor.execute(
            '''
            select * from tweets
            '''
        )
        for row in cursor.fetchall():
            tweetlist.append(row)
        return tweetlist


def maketweetbloblist(twtlist):
    twtbloblist = []
    for twt in twtlist:
        twttextblob = TextBlob(cleantweettext(twt[3]))
        twtdatetime = tu.stringtodate(twt[2])
        twtbloblist.append( (twt[0], twt[1], twtdatetime, twttextblob) )
    return twtbloblist


def getsimilar(reftwtblob, twtbloblist):
    simtwts = [reftwtblob]
    for twtblob in twtbloblist:
        if  ((reftwtblob[2] - twtblob[2]).total_seconds() <= 64800 and 
             reftwtblob[1] != twtblob[1]):
            ratio = fuzz.token_sort_ratio(reftwtblob[3].string, twtblob[3].string)
            if ratio >= 75 and ratio < 90:
                simtwts.append(twtblob)
    return simtwts


def savetweetgroup(simtwts):
    conn = sqlite3.connect(config.dbfile)
    with conn:
        c = conn.cursor()
        group_id = uuid.uuid4().hex
        for tweet in simtwts:
            c.execute(
                '''
                INSERT INTO tweetgroups (group_id, tweet_id) 
                VALUES (?, ?)
                ''',
                (group_id, tweet[0])
            )
    conn.close()



## Main ##

def main():
    print('\n')
    print('Retrieving and processing tweets from database...\n')
    twtbloblist = maketweetbloblist(retrievetweets())
    print('Processing tweets...\n')
    tweetnum = 1
    tweetcount = len(twtbloblist)
    while twtbloblist:
        reftwtblob = twtbloblist.pop()
        simtwts = getsimilar(reftwtblob, twtbloblist)
        if(len(simtwts) > 2):
            pprint(simtwts)
            print('\n')
            savetweetgroup(simtwts)
            print('Tweet group saved.\n')
            print(round(tweetnum * 100 / tweetcount), 'percent processed.\n')
        tweetnum += 1



if __name__ == "__main__":
    sys.exit(main())
