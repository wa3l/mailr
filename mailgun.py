from api_keys import APIKeys
import urllib2, urllib

class Mailgun():
  """
  Wrapper for Mailgun

  Automatically handles creating a request to the Mailgun service
  provided a email object that contains email data.
  """

  def __init__(self):
    """
    Initiate the object with the proper API keys.
    """
    self.key = APIKeys.MAILGUN_KEY
    self.url = APIKeys.MAILGUN_URL


  def authenticate(self):
    """
    Authenticate to the Mailgun service using our API keys.
    This is ugly code due to urllib's low levelness.
    """
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, self.url, 'api', self.key)
    # build a basic HTTP auth handler
    # build an opener with it and finally install it:
    auth   = urllib2.HTTPBasicAuthHandler(password_manager)
    opener = urllib2.build_opener(auth)
    urllib2.install_opener(opener)


  def send(self, email):
    """
    Send the email using the provided email dict.
    """
    self.authenticate()
    data =  {
              "from": "{0} <{1}>".format(email['from_name'], email['from']),
              "to":   "{0} <{1}>".format(email['to_name'],   email['to']),
              "subject": email['subject'],
              "text": email['text'],
              "html": email['html']
            }
    request = urllib2.Request(self.url, urllib.urlencode(data))
    handler = urllib2.urlopen(request)
    return handler.read()
