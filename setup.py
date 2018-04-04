# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages
import os

base_name='intweet'

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name=base_name,
    version='1.0',
    author=u'Leon Young',
    author_email='YoungL@github',
    include_package_data = True,
    packages=find_packages(), # include all packages under this directory
    description='to update',
    long_description="",
    zip_safe=False,

    package_data={'/intweet/templates':['*'],},

    # Adds dependencies
    install_requires = ['certifi',
                        'chardet',
                        'click',
                        'decorator',
                        'dominate',
                        'flask',
                        'flask-bootstrap',
                        'idna',
                        'itsdangerous',
                        'jinja2',
                        'pymysql',
                        'nltk',
                        'numpy',
                        'oauthlib',
                        'pep8',
                        'PySocks',
                        'requests',
                        'requests-oauthlib',
                        'six',
                        'sqlalchemy',
                        'tweepy',
                        'urllib3',
                        'validators',
                        'visitor',
                        'werkzeug',
                        ]
)

