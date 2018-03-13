import tweepy
from config import *
from database import get_db_session
from models.rule import Rule
from models.user import User
from models.tweet import Tweet
import time


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    session = get_db_session()
    query = session.query(Rule).join(User).filter(Rule.userid==User.id, Rule.active==1, User.active==1)

    rules = query.all()
    for rule in rules:
        for keyword in rule.keywords.split(", "):
            results = api.search(q=keyword)
            for result in results:
                text = result.text.encode(errors='ignore').\
                    decode('utf-32', 'ignore')
                location = result.user.location.encode(errors='ignore').\
                    decode('utf-32', 'ignore')
                tweet = Tweet(timestamp=result.created_at,
                              tweet=text, location=location, from_screenname=result.user.screen_name,
                              ruleid=rule.id,
                              profile_image_url=result.user.profile_image_url, profile_image_url_https=result.user.\
                              profile_image_url_https,
                              following=result.user.following, no_of_followers=result.user.followers_count,
                              contacted=0, tweet_id=result.id, trained=0)
                session.add(tweet)
                session.commit()
