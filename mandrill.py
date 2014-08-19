import os, urllib2, urllib, datetime, time
from flask import json

class Mandrill():
  """
  Wrapper for Mandrill

  Automatically handles creating a request to the Mandrill service
  provided a email object that contains email data.
  """
  key = os.environ['MANDRILL_KEY']
  url = os.environ['MANDRILL_URL']
  success = {
    'status':  'success',
    'message': 'Email queued to be sent by Mandrill.'
  }

  def __get_json_object(self, email):
    """
    Build a json-encoded object to be sent to Mandrill.
    """
    data = {
      'key': self.key,
      'message': {
        'from_email': email.from_email,
        'from_name':  email.from_name,
        'to': [{
          'email': email.to_email,
          'name':  email.to_name,
          'type':  'to'
        }],
        'subject':  email.subject,
        'html':     email.html,
        'text':     email.text,
        'attachments': [{}]
      }
    }
    if email.deliverytime > time.time():
      # construct time in YYYY-MM-DD HH:MM:SS format.
      # Note: no need to worry about float() throwing
      # an exception, validation has already done that.
      timestamp        = float(email.deliverytime)
      utc_datetime     = datetime.datetime.utcfromtimestamp(timestamp)
      data['send_at']  = utc_datetime.strftime('%Y-%m-%d %H:%M:%S')

    return json.dumps(data)


  def send(self, email):
    """
    Send the email using the provided email dict.
    """
    data    = self.__get_json_object(email)
    header  = {'Content-Type': 'application/json'}
    request = urllib2.Request(self.url, data, headers=header)
    # Note: Mandrill appears to be responding with 500 error code for any error.
    try:
      handler = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
      return (e.reason, e.code)

    return (self.success, handler.getcode())
