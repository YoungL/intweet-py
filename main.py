#!/usr/bin/env python

from models.user import User
from models.tweet import Tweet
from models.rule import Rule
from database import get_db_session
from crypt import crypt
from sqlalchemy import exc
from sqlalchemy.dialects import mysql

session = get_db_session()
if session.query(User).filter(User.email=="leontest@10.com").count() == 0:
    myuser = User(fullname='leon', email='leontest@10.com', password='password', admin=1)
    session.add(myuser)
    session.commit()
    print myuser.id
else:
    print "Email address taken"

query = session.query(User).filter(User.email=="leon@test9.com")
user = query.one()
print user.validate_password('password')

query = session.query(Tweet).filter(Tweet.timestamp=="1381824130")
tweet = query.one()

print tweet.id


query = session.query(Rule).join(User).filter(Rule.userid==User.id)
print str(query.statement.compile(dialect=mysql.dialect()))
rules = query.all()
for rule in rules:
    print "rule: %s, fullname: %s" % (rule.rulename, rule.user.fullname)
