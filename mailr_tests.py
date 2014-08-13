import mailr
import unittest
from flask import json

class MailrTestCase(unittest.TestCase):

  def setUp(self):
    mailr.app.config['TESTING'] = True
    self.app  = mailr.app.test_client()
    self.json = "{\"to\":\"wael@gmail.com\",\"from\":\"wael2@gmail.com\",\"to_name\":\"Wael Al-Sallami\",\"from_name\":\"Katie Lea\",\"subject\":\"A message from Uber\",\"body\":\"<h1>Your Bill</h1><p>$10</p>\"}"


  def test_accepts_no_get_requests(self):
    resp = self.app.get('/email')
    self.assertEqual(resp.status_code, 405)
    self.assertEqual(resp.status, "405 METHOD NOT ALLOWED")


  def test_rejects_non_json(self):
    resp = self.app.post('/email',
                        data="This is not json!",
                        content_type='application/json')
    self.assertEqual(resp.status_code, 400)
    self.assertIn('BAD REQUEST', resp.status)

  def test_rejects_invalid_json(self):
    resp = self.app.post('/email',
                        data=json.dumps("{\"to\":\"wael@gmail.com\"}"),
                        content_type='application/json')
    self.assertEqual(resp.status_code, 400)
    self.assertEqual('application/json', resp.headers[0][1])
    self.assertIn('BAD REQUEST', resp.status)


  def test_accepts_valid_json(self):
    resp = self.app.post('/email',
                        data=json.dumps(self.json),
                        content_type='application/json')
    self.assertEqual(resp.status_code, 200)
    self.assertEqual('application/json', resp.headers[0][1])
    self.assertIn('OK', resp.status)


if __name__ == '__main__':
    unittest.main()
