from database import BASE
from sqlalchemy import Column, Integer, String

class User(BASE):
    __tablename__ = 'tbl_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String)
    email = Column(String)
    password = Column(String)
    salt = Column(String)
    admin = Column(Integer)
