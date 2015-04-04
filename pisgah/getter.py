import sys
import random
import time
import sqlite3
import twitter
import config
import textutils as tu


## Setup ## 

# make Twitter api object
twitter_auth = twitter.oauth.OAuth(
    config.twitter_token, 
    config.twitter_token_secret,
    config.twitter_key, 
    config.twitter_secret)
twitter_api = twitter.Twitter(auth=twitter_auth)


# list of news source screen names
news_sources = [
    'nytimes', 'washingtonpost', 'cnn',
    'abc', 'cbsnews', 'nbcnews',
    'wsj', 'reuters', 'foxnews', 'ap',
    'nprnews'
]
    


## Database Functions ##

def savetweets(parsedtweets):
    conn = sqlite3.connect(config.dbfile)
    with conn:
        c = conn.cursor()
        for tweet in parsedtweets:
            try:  #TODO change this to insert or ignore?
                c.execute(
                    '''
                    INSERT INTO tweets (tweet_id, screen_name, tweet_time, tweet_text) 
                    VALUES (?, ?, ?, ?)
                    ''',
                    tweet
                )
            except sqlite3.IntegrityError:  # error if tweet_id exists
                continue
    conn.close()


def newestsavedtweet(sname):
    conn = sqlite3.connect(config.dbfile)
    with conn:
        c = conn.cursor()
        c.execute(
            '''
            SELECT MAX(tweet_id) from tweets WHERE screen_name = ?
            ''',
            (sname,)
        )
        newestid = c.fetchone()[0]
        return newestid



## Tweet Retrieval Functions ##


# parse raw tweets: extract useful info.
def parsetweets(rawtweets):
    parsedtweets = []
    for tweet in rawtweets:
        try:
            twtid = int(tweet['id'])
            sname = tweet['user']['screen_name'].lower()
            twttime = tu.normdatestring(tweet['created_at'])
            twttext = tweet['text']
        except Exception as e:
            print('parsetweets() response parsing error:', e)
        else:
            parsedtweets.append((twtid, sname, twttime, twttext))
    return parsedtweets


# get list of tweets from screen name
def getalltweets(sname):
    rawtweets = []
    firstbatch = True
    for i in range(20):  # break will probably occur before i == 20
        print('Getting batch', i)
        if firstbatch:
            res = twitter_api.statuses.user_timeline(
                count=200,
                screen_name=sname,
                exclude_replies=True,
                include_rts=False
            )
            firstbatch = False
        else:
            res = twitter_api.statuses.user_timeline(
                count=200,
                screen_name=sname,
                exclude_replies=True,
                include_rts=False,
                max_id=maxid
            )
        try:
            maxid = int(res[-1]['id']) - 1
        except IndexError as e:
            # break if Twitter response empty (no more tweets);
            print('Empty response received; ending batch retrieval')
            break
        else:
            rawtweets.extend(res)
            time.sleep(5) # 5 sec pause keeps us at 180 calls / 15 mins             
    return rawtweets



## Main ##

def main():
    alltwts = []
    random.shuffle(news_sources)
    for sname in news_sources:
        print('Getting tweets for', sname)
        twts = parsetweets(getalltweets(sname))
        print('Saving tweets for', sname)
        savetweets(twts)
        print('Done\n')
    return 0


if __name__ == "__main__":
    sys.exit(main())
