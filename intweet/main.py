import logging
import sys
from intweet.models.user import User
from intweet.models.tweet import Tweet
from intweet.models.rule import Rule
from intweet.database import get_db_session
from sqlalchemy.dialects import mysql


logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)


session = get_db_session()
if session.query(User).filter(User.email == "leontest@10.com").count() == 0:
    myuser = User(
        fullname='leon',
        email='leontest@10.com',
        password='password',
        admin=1
    )
    session.add(myuser)
    session.commit()
    logging.info(myuser.id)
else:
    logging.info("Email address taken")

query = session.query(User).filter(User.email == "leon@test9.com")
user = query.one()
logging.info(user.validate_password('password'))

query = session.query(Tweet).filter(Tweet.timestamp == "1381824130")
tweet = query.one()

logging.info(tweet.id)


query = session.query(Rule).join(User).filter(Rule.userid == User.id)
logging.info(str(query.statement.compile(dialect=mysql.dialect())))
rules = query.all()
for rule in rules:
    logging.info("rule: %s, fullname: %s" % (rule.rulename, rule.user.fullname))
