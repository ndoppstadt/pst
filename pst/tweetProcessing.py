from .models import Tweet, TwitterUser, Politician
from textblob import TextBlob 
from textblob.sentiments import NaiveBayesAnalyzer
from django.db.models import Count
import re 
import logging

def processTweet(politician_id, tweet):
    userId = getUserId(tweet)
    tweetId = getTweetId(tweet)
    print('inside process tweet')
    if userExists(userId) and not tweetExists(tweetId):

        print(" user exists and tweet does not exist")
        saveNewTweet(tweet, politician_id)
        incrementTweetCountForUser(userId)
    elif not userExists(userId):
        print("user exists")
        saveNewUser(tweet)
        saveNewTweet(tweet, politician_id)


def saveNewUser(tweet):
    try:
        user = TwitterUser(user_id = getUserId(tweet), username=getUsername(tweet), tweet_count = 1, user_full_name = getUserFullName(tweet), user_icon = getUserIcon(tweet), followers_count = getFollowers(tweet))
        user.save()
        print('New user Saved with ID ' + str(user.user_id))
    except Exception as e:
        print('User not saved with error ' + str(e))

def incrementTweetCountForUser(userId):
    try:
        twitterUser = TwitterUser.objects.get(user_id = userId)
        count = Tweet.objects.filter(twitterUser = twitterUser).count()
        twitterUser.tweet_count = count
        twitterUser.save()
        print("Twitter count for user id " + str(twitterUser.pk) + " is incremented to " + str(count))
    except Exception as e:
        print("User " + str(userId) + "count not incremented with error " + str(e))

def saveNewTweet(tweet, politician_id):
    try: 
        print("saving new tweet")
        twitterUser = TwitterUser.objects.get(user_id = getUserId(tweet))
        politician = Politician.objects.get(id=politician_id)
        tweet = Tweet(text = getText(tweet), twitterUser = twitterUser, is_retweet=getIsRetweet(tweet), 
        date=getDate(tweet), location=getLocation(tweet), sentiment=getSentimentPolarity(tweet), tweet_id=getTweetId(tweet), 
        politician=politician)
        tweet.save()
        print('Tweet successfully saved')
    except Exception as e:
        print('tweet not saved with error ' + str(e))
  
def userExists(userId):
    userCount = TwitterUser.objects.filter(user_id=userId).count()
    return False if userCount == 0 else True
   
def tweetExists(tweetId):
    tweetCount = Tweet.objects.filter(tweet_id = tweetId).count()
    return False if tweetCount == 0 else True

def getUserId(tweet):
    return tweet['user']['id']

def getDate(tweet):
    return tweet['created_at']

def getUsername(tweet):
    return tweet['user']['screen_name']

def getIsRetweet(tweet):
    return 'retweeted_status' in tweet 

def getTweetId(tweet):
    return tweet['id_str']

def getFollowers(tweet):
    return tweet['user']['followers_count'] 

def getLocation(tweet):
    location = ''
    if tweet['place'] is not None:
        location = tweet['place']['full_name']
    return location

            
def getUserIcon(tweet):
    return tweet['user']['profile_image_url_https'] 

def clean_tweet(tweet):
    '''
    Utility function to clean the text in a tweet by removing 
    links and special characters using regex.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


def getSentimentPolarity(tweet):
    analysis = TextBlob(clean_tweet(tweet['full_text']))
    # getSentimentClassification(tweet)
    # getSentimentSubjectivity(analysis)
    return analysis.sentiment.polarity

def getSentimentSubjectivity(analysis): 
    return analysis.subjectivity

def getSentimentClassification(tweet): 
    analysis = TextBlob(tweet['full_text'], analyzer=NaiveBayesAnalyzer())
    return analysis.sentiment

def getText(tweet):
    tweettext = ""
    if 'retweeted_status' in tweet:
        tweettext = tweet['retweeted_status']['full_text']
    elif 'full_text' in tweet:
        tweettext = tweet['full_text']
    else:
        print('Tweet text cannot be found')
    # print("Tweet text saved is " + tweettext)
    return tweettext


def getUserFullName(tweet):
    try:
        return tweet['user']['name']
    except:
        return "Username Error"

