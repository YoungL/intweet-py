from intweet.database import BASE
from sqlalchemy import Column, Integer


class TrainCache(BASE):
    __tablename__ = 'tbl_train_count_live'

    sentiment = Column(Integer, primary_key=True)
    qty = Column(Integer, nullable=False)
