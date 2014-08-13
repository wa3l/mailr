import urllib2, urllib, logging
from flask    import json
from urllib2  import HTTPError
from api_keys import APIKeys

class Mailgun():
  """
  Wrapper for Mailgun

  Automatically handles creating a request to the Mailgun service
  provided a email object that contains email data.
  """
  key = APIKeys.MAILGUN_KEY
  url = APIKeys.MAILGUN_URL
  success = {
    'status':  'success',
    'message': 'Email queued to be sent by Mailgun.'
  }

  def __get_encoded_object(self, data):
    """
    Build a url-encoded object to be sent to Mailgun.
    """
    return urllib.urlencode({
      'from':     '{0} <{1}>'.format(data['from_name'], data['from']),
      'to':       '{0} <{1}>'.format(data['to_name'],   data['to']),
      'subject':  data['subject'],
      'text':     data['text'],
      'html':     data['html']
    })


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



  def send(self, data):
    """
    Send the email using the provided email dict.
    First authenticate to Mailgun, then build the request object and send it
    """
    self.authenticate()
    data    = self.__get_encoded_object(data)
    request = urllib2.Request(self.url, data)
    try:
      handler = urllib2.urlopen(request)
    except HTTPError as e:
      return (e.reason, e.code)

    return (self.success, handler.getcode())
