from intweet.database import BASE
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property


class Features(BASE):
    __tablename__ = 'tbl_features_live'

    feature = Column(String, primary_key=True)
    sentiment = Column(Integer, primary_key=True)
    count = Column(Integer, nullable=False)
