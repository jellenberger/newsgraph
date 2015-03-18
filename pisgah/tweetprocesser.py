import sys
import re
import uuid
import sqlite3
from fuzzywuzzy import fuzz
import config
import textutils as tu

# dev imports
import random
from pprint import pprint



def clean_tweettext(twttext):
    twttext = tu.asciichars(twttext) # ascii chars only
    twttext = tu.normspace(twttext) # whitespace chars to spaces
    twttext = tu.unescape(twttext) # fix url encoded text
    twttext = tu.rmurls(twttext) # remove urls
    twttext = twttext.replace('-', '') # - to space
    twttext = twttext.replace('_', '') # _ to space
    twttext = twttext.replace('#', '') # no #
    twttext = twttext.replace('@', '') # no @
    twttext = re.sub(': *$', '', twttext) # no colon + space* at end
    twttext = re.sub('', '', twttext).strip() # single spaces only
    return twttext


def retrieve_tweets():
    with sqlite3.connect(config.dbfile) as conn:
        twtlist = []
        cursor = conn.cursor()
        cursor.execute(
            '''
            select * from tweets
            '''
        )
        for row in cursor.fetchall():
            twtlist.append(row)
        return twtlist


def process_tweetlist(twtlist):
    outlist = []
    for twt in twtlist:
        twttext = clean_tweettext(twt[3])
        twtdatetime = tu.stringtodate(twt[2])
        outlist.append( (twt[0], twt[1], twtdatetime, twttext) )
    return outlist


def find_similartweets(reftwt, twtlist):
    simtwts = [reftwt]
    for twt in twtlist:
        if  ((reftwt[2] - twt[2]).total_seconds() <= 64800 and 
             reftwt[1] != twt[1]):
            ratio = fuzz.token_sort_ratio(reftwt[3], twt[3])
            if ratio >= 75 and ratio < 90:
                simtwts.append(twt)
    return simtwts


def save_tweetgroup(simtwts):
    conn = sqlite3.connect(config.dbfile)
    with conn:
        c = conn.cursor()
        group_id = tu.baseencode(uuid.uuid4().int)
        for twt in simtwts:
            c.execute(
                '''
                INSERT INTO tweetgroups (group_id, tweet_id, screen_name, tweet_time, cleantext) 
                VALUES (?, ?, ?, ?, ?)
                ''',
                (group_id, twt[0], twt[1], twt[2].strftime('%Y-%m-%d %H:%M:%S'), twt[3])
            )
    conn.close()



## Main ##

def main():
    print('\n')
    print('Retrieving tweets from database.\n')
    twtlist = retrieve_tweets()
    print('Processing tweets.\n')
    twtlist = process_tweetlist(twtlist)
    print('Finding similar tweet groups.\n')
    twtnum = 1
    twtcount = len(twtlist)
    while twtlist:
        reftwt = twtlist.pop()
        simtwts = find_similartweets(reftwt, twtlist)
        if(len(simtwts) > 2):
            pprint(simtwts)
            print('\n')
            save_tweetgroup(simtwts)
            print('Tweet group saved.\n')
            print(round(twtnum * 100 / twtcount), 'percent processed.\n')
        twtnum += 1


if __name__ == "__main__":
    sys.exit(main())
