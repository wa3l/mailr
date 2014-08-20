from os.path import abspath, dirname, join
import os

_cwd = dirname(abspath(__file__))


class BaseConfig(object):
  DEBUG     = False
  TESTING   = False
  PAGE_SIZE = 20
  SERVICES  = ['mailgun', 'mandrill']
  MAILGUN_KEY             = os.environ['MAILGUN_KEY']
  MAILGUN_URL             = os.environ['MAILGUN_URL']
  MANDRILL_KEY            = os.environ['MANDRILL_KEY']
  MANDRILL_URL            = os.environ['MANDRILL_URL']
  MAILR_KEY               = os.environ['MAILR_KEY']

class TestConfig(BaseConfig):
  TESTING                 = True
  WTF_CSRF_ENABLED        = False
  SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProdConfig(BaseConfig):
  SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

class DevConfig(ProdConfig):
  DEBUG = True
