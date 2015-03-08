import sys
import time
import csv
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
            res = twitter_api.statuses.user_timeline(
                count=200,
                screen_name=sname,
                include_rts=False,
                max_id=maxid
            )
        maxid = int(res[-1]['id']) - 1
        rawtweets.extend(res)
        print('Pausing 5 seconds.')
        time.sleep(5)
    return rawtweets


# parse raw tweets: extract useful info., basic cleanup
def parsetweets(rawtweets):
    parsedtweets = []
    for tweet in rawtweets:
        tweetid = int(tweet['id'])
        screen_name = tweet['user']['screen_name'] 
        date = tu.normdatestring(tweet['created_at'])
        text = tweet['text']
        text = tu.asciichars(text)
        text = tu.normspace(text)
        text = tu.unescape(text)
        parsedtweets.append((tweetid, screen_name, text, date))
    return parsedtweets



## Main ##

def main():
    alltwts = []
    for sname in news_sources:
        print('Getting tweets for', sname)
        alltwts.extend(parsetweets(gettweets(sname)))
        print('Done')
        print('Current count:', len(alltwts), 'tweets')
    print('Writing to file')
    with open('tweets.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(alltwts)
    print('Done')
    return 0


if __name__ == "__main__":
    sys.exit(main())
