from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config
import logging
#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

BASE = declarative_base()

def get_db_engine():
    engine = create_engine(config.DB_URL, echo=config.DEBUG)
    return engine

def get_db_session():
    sessmaker = sessionmaker(bind=get_db_engine())
    session = sessmaker()
    return session

def init_db():
    BASE.metadata.create_all(get_db_engine())

init_db()
