import os, urllib2, urllib, time
from flask import json

class Mailgun():
  """
  Wrapper for Mailgun

  Automatically handles creating a request to the Mailgun service
  provided a email object that contains email data.
  """
  key = os.environ['MAILGUN_KEY']
  url = os.environ['MAILGUN_URL']
  success = {
    'status':  'success',
    'message': 'Email queued to be sent by Mailgun.'
  }

  def __get_encoded_object(self, email):
    """
    Build a url-encoded object to be sent to Mailgun.
    """
    data = {
      'from':     '{0} <{1}>'.format(email.from_name, email.from_email),
      'to':       '{0} <{1}>'.format(email.to_name,   email.to_email),
      'subject':  email.subject,
      'text':     email.text,
      'html':     email.html
    }
    if email.deliverytime > time.time():
      data['o:deliverytime'] = email.deliverytime

    return urllib.urlencode(data)


  def authenticate(self):
    """
    Authenticate to the Mailgun service using our API keys.
    This is ugly code due to urllib's low levelness. It:
      1. Creates a password manager and configures it.
      2. Builds a Basic HTTP Auth handler.
      3. Builds an opener and instalsl it.
    """
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, self.url, 'api', self.key)
    auth   = urllib2.HTTPBasicAuthHandler(password_manager)
    opener = urllib2.build_opener(auth)
    urllib2.install_opener(opener)



  def send(self, email):
    """
    Send the email using the provided email dict.
    First authenticate to Mailgun, then build the request object and send it
    """
    self.authenticate()
    data    = self.__get_encoded_object(email)
    request = urllib2.Request(self.url, data)
    try:
      handler = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
      return (e.reason, e.code)

    return (self.success, handler.getcode())
