from database import BASE
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property

class TrainCache(BASE):
    __tablename__ = 'tbl_train_count_live'
    
    sentiment = Column(Integer, primary_key=True)
    qty = Column(Integer, nullable=False)