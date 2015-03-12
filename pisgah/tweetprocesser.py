import sys
import re
import sqlite3
from textblob import TextBlob
import config
import random # temp?


def cleantweettext(twttext):
    # delete urls
    twttext = re.sub('(([\w-]+://?|www[.])[^\s()<>]+)', '', twttext)
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


def tagtweets(twtlist):
    for twt in twtlist:
        twttext = twt[3]
        twtblob = TextBlob(cleantweettext(twttext))
        print(twtblob.tags)
        

## Main ##

def main():
    twtlist = random.sample(retrievetweets(), 5)
    print(tagtweets(twtlist))


if __name__ == "__main__":
    sys.exit(main())
