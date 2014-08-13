import mailr
from helpers import *
import unittest
from mailgun import Mailgun
from mandrill import Mandrill
import html2text as convert

class HelpersTestCase(unittest.TestCase):

  def setUp(self):
    mailr.app.config['TESTING'] = True
    self.app  = mailr.app.test_client()


  def test_returns_correct_provider(self):
    self.assertIsInstance(email_service('Mailgun'), Mailgun)
    self.assertIsInstance(email_service('Mandrill'), Mandrill)
    with self.assertRaises(ImportError):
      email_service('WrongClass')


  def test_converts_body(self):
    html = '<h1>Your Bill</h1><p>$10</p>'
    data = {'body': html}
    data = convert_body(data)
    self.assertEqual(data['html'], html)
    self.assertEqual(data['text'], convert.html2text(html))
    self.assertFalse(data.has_key('body'))


if __name__ == '__main__':
    unittest.main()
