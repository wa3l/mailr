from flask.ext.sqlalchemy import SQLAlchemy
import html2text as convert
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
  service      = db.Column(db.String(10))
  deliverytime = db.Column(db.BigInteger)


  def __init__(self, data):
    self.to_email   = data['to']
    self.to_name    = data['to_name']
    self.from_email = data['from']
    self.from_name  = data['from_name']
    self.subject    = data['subject']
    self.html       = data['body']
    self.text       = convert.html2text(data['body'])
    self.service    = data['service'] if data.has_key('service') else None
    if data.has_key('deliverytime'):
      self.deliverytime = int(data['deliverytime'])
    else:
      self.deliverytime = int(time.time())


  def __str__(self):
    return str({
      'to':           self.to_email,
      'from':         self.from_email,
      'to_name':      self.to_name,
      'from_name':    self.from_name,
      'subject':      self.subject,
      'text':         self.text,
      'html':         self.html,
      'service':     self.service,
      'deliverytime': str(self.deliverytime)
    })


  def __repr__(self):
    return str(self)
