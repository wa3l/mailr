from flask.ext.sqlalchemy import SQLAlchemy
import time

db = SQLAlchemy()

class Email(db.Model):
  """
  Email model
  Store emails going through the app in a database.
  """
  id           = db.Column(db.Integer, primary_key=True)
  to_email     = db.Column(db.String(254))
  to_name      = db.Column(db.String(256))
  from_email   = db.Column(db.String(254))
  from_name    = db.Column(db.String(256))
  subject      = db.Column(db.String(78))
  html         = db.Column(db.UnicodeText)
  text         = db.Column(db.UnicodeText)
  provider     = db.Column(db.String(10))
  deliverytime = db.Column(db.BigInteger)


  def __init__(self, email):
    self.to_email   = email['to']
    self.to_name    = email['to_name']
    self.from_email = email['from']
    self.from_name  = email['from_name']
    self.subject    = email['subject']
    self.html       = email['html']
    self.text       = email['text']
    self.provider   = email['provider']
    if email.has_key('deliverytime'):
      self.deliverytime = int(email['deliverytime'])
    else:
      self.deliverytime = int(time.time())
