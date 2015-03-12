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
    'nytimes', 'washingtonpost', 'CNN',
    'ABC', 'CBSNews', 'NBCNews',
    'WSJ', 'Reuters', 'FoxNews', 'AP'
]


## Tweet Retrieval ##

# get list of tweets from screen name
def gettweets(sname):

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
            time.sleep(5)
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
            # caused by an empty Twitter response (no more tweets available);
            # break out of loop
            print('Empty response received. Ending batch retrieval.')
            break
        else:
            rawtweets.extend(res)            
    return rawtweets


# parse raw tweets: extract useful info., basic cleanup
def parsetweets(rawtweets):
    parsedtweets = []
    for tweet in rawtweets:
        try:
            twtid = int(tweet['id'])
            sname = tweet['user']['screen_name'] 
            twttime = tu.normdatestring(tweet['created_at'])
            twttext = tweet['text']
        except Exception as e:
            print('parsetweets() response parsing error:', e)
        else:
            twttext = tu.asciichars(twttext)
            twttext = tu.normspace(twttext)
            twttext = tu.unescape(twttext)
            parsedtweets.append((twtid, sname, twttime, twttext))
    return parsedtweets


def savetweets(parsedtweets):
    conn = sqlite3.connect(config.dbfile)
    with conn:
        c = conn.cursor()
        for tweet in parsedtweets:
            try:  #TODO change this to insert or ignore?
                c.execute(
                    '''
                    INSERT INTO tweets (twtid, sname, twttime, twttext) 
                    VALUES (?, ?, ?, ?)
                    ''',
                    tweet
                )
            except sqlite3.IntegrityError:  # error caused if twtid exists
                continue
    conn.close()



## Main ##

def main():
    alltwts = []
    for sname in news_sources:
        print('Getting tweets for', sname)
        twts = parsetweets(gettweets(sname))
        print('Saving tweets for', sname)
        savetweets(twts)
        print('Done')
    return 0


if __name__ == "__main__":
    sys.exit(main())
