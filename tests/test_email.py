from test_base import BaseTestCase
from email_model import Email
from flask import json
from flask import jsonify


class MailrEmailTests(BaseTestCase):

  def test_rejects_get_requests(self):
    resp = self.client.get('/email')
    self.assert_405(resp)


  def test_only_accepts_json_data(self):
    resp = self.client.post('/email',
                            data="This is not valid json!",
                            content_type='application/json')
    self.assert_400(resp)
    self.assertIn('Invalid JSON request.', resp.data)


  def test_demands_required_fields(self):
    data = self.sample_email()
    data.pop('to')
    resp = self.client.post('/email',
                            data=json.dumps(data),
                            content_type='application/json')
    self.assert_400(resp)
    self.assertIn('required key not provided', resp.data)


  def test_doesnt_demand_optional_fields(self):
    data = self.sample_email()
    data.pop('service')
    resp = self.client.post('/email',
                            data=json.dumps(data),
                            content_type='application/json')
    self.assert_200(resp)
    self.assertIn('Email queued to be sent by', resp.data)


  def test_sends_emails_properly(self):
    data = self.sample_email()
    data.pop('service')
    data.pop('deliverytime')
    resp = self.client.post('/email',
                            data=json.dumps(data),
                            content_type='application/json')
    self.assert_200(resp)
    self.assertIn('Mailgun', resp.data)


  def test_sends_with_specified_service(self):
    data = self.sample_email()
    data['service'] = 'mandrill'
    resp = self.client.post('/email',
                            data=json.dumps(data),
                            content_type='application/json')
    self.assert_200(resp)
    self.assertIn('Mandrill', resp.data)
