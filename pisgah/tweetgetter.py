import sys
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
    'ABC', 'CBSNews', 'NBCNews',
    'WSJ', 'Reuters', 'FoxNews', 'AP'
]


## Tweet Retrieval ##

# get list of tweets from screen name
def gettweets(sname):
    rawtweets = []
    firstbatch = True
    for _ in range(4):
        if firstbatch:
            res = twitter_api.statuses.user_timeline(
                count=200,
                screen_name=sname,
                include_rts=False
            )
            firstbatch = False
        else:
            print('Pausing 5 seconds.')
            time.sleep(5)
            res = twitter_api.statuses.user_timeline(
                count=200,
                screen_name=sname,
                include_rts=False,
                max_id=maxid
            )
        maxid = int(res[-1]['id']) - 1
        rawtweets.extend(res)
    return rawtweets


# parse raw tweets: extract useful info., basic cleanup
def parsetweets(rawtweets):
    parsedtweets = []
    for tweet in rawtweets:
        twtid = int(tweet['id'])
        sname = tweet['user']['screen_name'] 
        twttime = tu.normdatestring(tweet['created_at'])
        twttext = tweet['text']
        twttext = tu.asciichars(twttext)
        twttext = tu.normspace(twttext)
        twttext = tu.unescape(twttext)
        parsedtweets.append((twtid, sname, twttime, twttext))
    return parsedtweets


def savetweets(parsedtweets):
    conn = sqlite3.connect('data/pisgahdata.db')
    with conn:
        c = conn.cursor()
        for tweet in parsedtweets:
            try:
                c.execute(
                    '''
                    INSERT INTO tweets (twtid, sname, twttime, twttext) 
                    VALUES (?, ?, ?, ?)
                    ''',
                    tweet
                )
            except sqlite3.IntegrityError:
                print('Tweet exists in database, skipping')
    conn.close()



## Main ##

def main():
    alltwts = []
    for sname in news_sources:
        print('Getting tweets for', sname)
        twts = parsetweets(gettweets(sname))
        print('Saving tweets')
        savetweets(twts)
        print('Done')
    return 0


if __name__ == "__main__":
    sys.exit(main())
