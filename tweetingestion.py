import tweepy
from config import *
from database import get_db_session
from models.rule import Rule
from models.user import User
from models.tweet import Tweet
import time

class TweetIngestion:

    def __init__(self, dbsession):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)
        self.session = dbsession

    def ingest_tweets(self, user_active=1, rule_active=1):
        query = self.session.query(Rule).join(User).\
            filter(Rule.userid==User.id, Rule.active==rule_active,
                   User.active==user_active)

        rules = query.all()

        for rule in rules:
            for keyword in rule.keywords.split(", "):
                results = self.api.search(q=keyword)
                for result in results:
                    self.commit_tweet_to_db(rule.id, result)

    def commit_tweet_to_db(self, ruleid, result):
        text = result.text.encode(errors='ignore').\
            decode('utf-32', 'ignore')
        location = result.user.location.encode(errors='ignore').\
            decode('utf-32', 'ignore')
        tweet = Tweet(timestamp=result.created_at,
                      tweet=text, location=location,
                      from_screenname=result.user.screen_name,
                      ruleid=ruleid,
                      profile_image_url=result.user.profile_image_url, profile_image_url_https=result.user.\
                      profile_image_url_https,
                      following=result.user.following, no_of_followers=result.user.followers_count,
                      contacted=0, tweet_id=result.id, trained=0)

        session.add(tweet)
        session.commit()

if __name__ == '__main__':
    session = get_db_session()
    tweetingestion = TweetIngestion(session)
    tweetingestion.ingest_tweets()
