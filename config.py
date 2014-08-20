from os.path import abspath, dirname, join
import os

_cwd = dirname(abspath(__file__))


class BaseConfig(object):
  DEBUG       = False
  TESTING     = False
  SECRET_KEY  = os.environ['MAILR_KEY']
  PAGE_SIZE   = 20

class TestConfig(BaseConfig):
  TESTING                 = True
  WTF_CSRF_ENABLED        = False
  SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class DevConfig(BaseConfig):
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

class ProdConfig(BaseConfig):
  SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
