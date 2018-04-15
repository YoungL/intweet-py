from intweet.database import BASE
from sqlalchemy import Column, Integer
from sqlalchemy.types import UnicodeText


class TrainData(BASE):
    __tablename__ = 'tbl_train_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_tweet = Column(UnicodeText, nullable=False)
    sentiment = Column(Integer, nullable=True)
