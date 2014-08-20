from flask.ext.testing import TestCase
from mailr import app, db
from werkzeug.test import Client
from werkzeug.datastructures import Headers
from base64 import b64encode
from email_model import Email
import os, base64, random, time
from flask import jsonify

class BaseTestCase(TestCase):
  """A base test case for flask-tracking."""

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


class MailrEmailsTests(BaseTestCase):

  def basic_auth(self, path, key, follow_redirects=True):
    h     = Headers()
    login = b64encode('api:{}'.format(key))
    h.add('Authorization', 'Basic {}'.format(login))
    return Client.open(self.client,
                       path=path,
                       headers=h,
                       follow_redirects=follow_redirects)


  def get_emails_dict(self, results):
    return {e.id: str(e) for e in results.items}


  def test_default_permanently_redirects(self):
    resp = self.client.get('/emails')
    self.assert_redirects(resp, '/emails/')


  def test_first_page_permanently_redirects(self):
    resp = self.client.get('/emails/1')
    self.assert_redirects(resp, '/emails/')


  def test_requires_basic_auth(self):
    resp = self.client.get('/emails/')
    self.assert_401(resp)


  def test_requires_correct_password(self):
    resp = self.basic_auth('/emails/2', 'wrong_password')
    self.assert_401(resp)


  def test_allows_valid_basic_auth(self):
    resp = self.basic_auth('/emails/2', self.key)
    self.assert_200(resp)


  def test_responds_with_json(self):
    resp = self.basic_auth('/emails/', self.key)
    self.assertEquals(resp.json, dict(emails=dict(), page=1))


  def test_responds_with_correct_page_number(self):
    page = random.randint(1, 100)
    resp = self.basic_auth('/emails/{}'.format(page), self.key)
    self.assertEquals(resp.json, dict(emails=dict(), page=page))


  def test_responds_with_saved_emails(self):
    self.create_n_emails(5)
    resp      = self.basic_auth('/emails/', self.key)
    results   = Email.query.paginate(1, 20, False)
    fake_resp = jsonify(page=1, emails=self.get_emails_dict(results))
    self.assertEquals(resp.json, fake_resp.json)


  def test_paginates_properly(self):
    self.create_n_emails(21)
    resp      = self.basic_auth('/emails/2', self.key)
    results   = Email.query.paginate(2, 20, False)
    fake_resp = jsonify(page=2, emails=self.get_emails_dict(results))
    self.assertEquals(resp.json, fake_resp.json)

