from intweet.database import BASE
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
import intweet.models.user


class Rule(BASE):
    __tablename__ = 'tbl_monitor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    rulename = Column(String, nullable=False)
    keywords = Column(String, nullable=False)
    description = Column(String, nullable=False)
    active = Column(Integer, nullable=False)
    parentrule = Column(Integer, nullable=True)
    account_handle = Column(String, nullable=False)
    userid = Column(Integer, ForeignKey("tbl_users.id"), nullable=False)
    user = relationship("User", foreign_keys=[userid])
