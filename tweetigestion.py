import tweepy
from config import *
from database import get_db_session
from models.rule import Rule
from models.user import User
from models.tweet import Tweet
import time
from sqlalchemy.dialects import mysql


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    session = get_db_session()
    query = session.query(Rule).join(User).filter(Rule.userid==User.id, Rule.active==1, User.active==1)

    print str(query.statement.compile(dialect=mysql.dialect()))

    rules = query.all()
    for rule in rules:
        for keyword in rule.keywords.split(", "):
            results = api.search(q=keyword)
            for result in results:
                print "---------------"
                print result.created_at
                print result.text
                print result.user.location
                print result.user.screen_name
                print rule.id
                print result.user.profile_image_url
                print result.user.profile_image_url_https
                print result.user.following
                print result.id
                print result.coordinates
                print "0"
                print "---------------"
                if result.coordinates == None:
                    coordinates = None
                else:
                    coordinates = coordinates['coordinates']
                tweet = Tweet(timestamp=result.created_at, tweet=result.text.encode(errors='ignore').decode('utf-32', 'ignore'), location=result.user.location.encode(errors='ignore').decode('utf-32', 'ignore'), from_screenname=result.user.screen_name, ruleid=rule.id, profile_image_url=result.user.profile_image_url, profile_image_url_https=result.user.profile_image_url_https, following=result.user.following, no_of_followers=result.user.followers_count, coordinates=coordinates, postprocess_tweet=result.text.encode(errors='ignore').decode('utf-32', 'ignore'), contacted=0, tweet_id=result.id, trained=0)
                session.add(tweet)
                session.commit()
                print "Result found and inserted"


    #timestamp = Column(Integer, nullable=False)
    ##tweet = Column(String, nullable=False)
    #location = Column(String, nullable=False)
    #from_screenname = Column(String, nullable=False)
    #ruleid = Column("rule", Integer, ForeignKey("tbl_monitor.id"), nullable=False)
    #profile_image_url = Column(String, nullable=False)
    #profile_image_url_https = Column(String, nullable=False)
    #following = Column(Integer, nullable=False)
    #tweet_id = Column(Integer, nullable=False)
    #trained = Column(Integer, nullable=False)
    #rule = relationship("Rule", foreign_keys=[ruleid])
