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
    twttext = twttext.replace('-', ' ') # - to space
    twttext = twttext.replace('_', ' ') # _ to space
    twttext = twttext.replace('#', '') # no #
    twttext = twttext.replace('@', '') # no @
    twttext = re.sub(': *$', '', twttext) # no colon + space* at end
    twttext = tu.singlespaces(twttext).strip() # single spaces only
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
    #TODO eliminate duplicates from added items
    simtwts = [reftwt]
    for twt in twtlist:
        if  (abs((reftwt[2] - twt[2])).total_seconds() <= 86400 and 
             reftwt[1] != twt[1]):
            ratio = fuzz.token_sort_ratio(reftwt[3], twt[3])
            if ratio >= 75 and ratio < 90:
                simtwts.append(twt)
    return simtwts



## DB Functions ##


def clear_groupstable():
    conn = sqlite3.connect(config.dbfile)
    with conn:
        c = conn.cursor()
        c.execute(
            '''
            DROP TABLE IF EXISTS tweetgroups
            '''
        )
        c.execute(
            '''
            CREATE TABLE tweetgroups(
            group_id text, tweet_id integer, screen_name text, 
            tweet_time datetime, cleantext text)
            '''
        )


def save_tweetgroup(simtwts):
    conn = sqlite3.connect(config.dbfile)
    with conn:
        c = conn.cursor()
        group_id = tu.baseencode(uuid.uuid4().int)
        for twt in simtwts:
            twttime = twt[2].strftime('%Y-%m-%d %H:%M:%S')
            c.execute(
                '''
                INSERT INTO tweetgroups
                (group_id, tweet_id, screen_name, 
                tweet_time, cleantext) 
                VALUES (?, ?, ?, ?, ?)
                ''',
                (group_id, twt[0], twt[1], twttime, twt[3])
            )
    conn.close()




## Main ##

def main():
    groupstablecleared = False
    print('\n')
    print('Retrieving tweets from database.\n')
    twtlist = retrieve_tweets()
    twtlist.reverse()
    print('Preparing tweets for processing.\n')
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
            # now that we're about to save groups data, clear table if first save
            if not groupstablecleared:
                print('Clearing tweet groups table.\n')
                clear_groupstable()
                groupstablecleared = True
            save_tweetgroup(simtwts)
            print('Tweet group saved.\n')
            print(round(twtnum * 100 / twtcount), 'percent processed.\n')
        twtnum += 1
    print('Done.\n')


if __name__ == "__main__":
    sys.exit(main())
