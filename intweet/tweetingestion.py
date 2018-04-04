import tweepy
from intweet.config import *
from intweet.database import get_db_session
from intweet.models.rule import Rule
from intweet.models.user import User
from intweet.models.tweet import Tweet
from intweet.sentiment_analyser import SentimentAnalyser
import time


class TweetIngestion:

    def __init__(self, dbsession):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)
        self.session = dbsession
        self.sentiment_analyser = SentimentAnalyser()

    def process_rules(self):
        query = self.session.query(Rule.id).join(User).filter(
            Rule.userid == User.id,
            Rule.active == 1,
            User.active == 1
        )
        rules = query.all()
        for rule in rules:
            self.ingest_tweet_for_rule(rule.id)

    def ingest_tweet_for_rule(self, ruleid):
        query = self.session.query(
            Rule.id,
            Rule.keywords,
            Tweet.tweet_id
        ).outerjoin(Tweet).filter(Rule.id == ruleid).\
            order_by(Tweet.tweet_id.desc()).limit(1)

        rule = query.one()
        for keyword in rule.keywords.split(", "):
            since_id = 0
            if rule.tweet_id > 0:
                since_id = rule.tweet_id

            results = self.api.search(q=keyword, since_id=since_id)
            for result in results:
                self.commit_tweet_to_db(ruleid, result)

    def commit_tweet_to_db(self, ruleid, result):
        text = result.text.encode(errors='ignore').\
            decode('utf-8', 'ignore')
        location = result.user.location.encode(errors='ignore').\
            decode('utf-8', 'ignore')
        sentiment = self.sentiment_analyser.multinomial_naive_bayes(str(text))
        tweet = Tweet(
            timestamp=result.created_at,
            tweet=text,
            location=location,
            from_screenname=result.user.screen_name,
            ruleid=ruleid,
            profile_image_url=result.user.profile_image_url,
            profile_image_url_https=result.user.profile_image_url_https,
            following=result.user.following,
            no_of_followers=result.user.followers_count,
            contacted=0,
            tweet_id=result.id,
            sentiment=sentiment,
            trained=0,
        )

        session.add(tweet)
        session.commit()

if __name__ == '__main__':
    session = get_db_session()
    tweetingestion = TweetIngestion(session)
    tweetingestion.process_rules()
