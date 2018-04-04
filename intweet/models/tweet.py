from intweet.database import BASE
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime, UnicodeText


class Tweet(BASE):
    __tablename__ = 'tbl_raw_tweets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    tweet = Column(UnicodeText, nullable=False)
    location = Column(String, nullable=False)
    no_of_followers = Column(Integer, nullable=False)
    from_screenname = Column(String, nullable=False)
    ruleid = Column(
        "rule", Integer, ForeignKey("tbl_monitor.id"),
        nullable=False
    )
    profile_image_url = Column(String, nullable=False)
    profile_image_url_https = Column(String, nullable=False)
    following = Column(Integer, nullable=False)
    tweet_id = Column(Integer, nullable=False)
    trained = Column(Integer, nullable=False)
    contacted = Column(Integer, nullable=False)
    sentiment = Column(Integer, nullable=True)
    rule = relationship("Rule", foreign_keys=[ruleid])
