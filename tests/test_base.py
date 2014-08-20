from flask.ext.testing import TestCase
from mailr import app, db
from email_model import Email
import time

class BaseTestCase(TestCase):
  """A base test case for mailr."""

  def create_app(self):
    app.config.from_object('config.TestConfig')
    self.key = app.config['SECRET_KEY']
    return app

  def setUp(self):
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()

  def email_data(self):
    return {
      u'to':           u't@test.com',
      u'to_name':      u'Person B',
      u'from':         u'f@test.com',
      u'from_name':    u'Person A',
      u'subject':      u'Test email',
      u'body':         u'<p>hello</p>',
      u'deliverytime': time.time()
    }

  def create_n_emails(self, n):
    for _ in xrange(n):
      data  = self.email_data()
      email = Email(data)
      db.session.add(email)
    db.session.commit()
