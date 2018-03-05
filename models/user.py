from database import BASE
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
import hashlib
from random import randint
import re
import string

class User(BASE):
    __tablename__ = 'tbl_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    admin = Column(Integer, nullable=False)
    email = Column("email", String)
    _password = Column("password", String, nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self.salt = self.generate_salt()
        self._password = hashlib.sha256(password + self.salt).hexdigest()

    @validates('email')
    def validate_email(self, key, email):
        if not re.match("[^@]+@[^@]+\.[^@]+", email):
            raise Exception("Invalid Email Address")
        return email

    def generate_salt(self):
        allchar = string.ascii_letters + string.punctuation + string.digits
        salt = "".join(choice(allchar) for x in range(randint(16, 16)))
        return salt

    def validate_password(self, password):
        if hashlib.sha256(password + self.salt).hexdigest() == self.password:
            return True
        return False
