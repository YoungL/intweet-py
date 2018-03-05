from database import BASE
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

class Tweet(BASE):
    __tablename__ = 'tbl_raw_tweets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Integer, nullable=False)
    tweet = Column(String, nullable=False)
    location = Column(String, nullable=False)
    from_screenname = Column(String, nullable=False)
    rule = Column(Integer, nullable=False)
    profile_image_url = Column(String, nullable=False)
    profile_image_url_https = Column(String, nullable=False)
    following = Column(Integer, nullable=False)
    tweet_id = Column(Integer, nullable=False)
    trained = Column(Integer, nullable=False)
