from intweet.database import BASE
from sqlalchemy import Column, Integer, String


class Features(BASE):
    __tablename__ = 'tbl_features_live'

    feature = Column(String, primary_key=True)
    sentiment = Column(Integer, primary_key=True)
    count = Column(Integer, nullable=False)
