#!/usr/bin/env python

from models.user import User
from database import get_db_session
from database import session


myuser = User(fullname='leon', email='leon@test.com', password='password', salt='blah', admin=1)
session.add(myuser)
session.commit()

print myuser.id

query = session.query(User).filter(User.email=="youngl234@gmail.com")
user = query.one()

print user.fullname
