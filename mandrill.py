from api_keys import APIKeys
import urllib2, urllib, json

class Mandrill():
  """
  Wrapper for Mandrill

  Automatically handles creating a request to the Mandrill service
  provided a email object that contains email data.
  """

  def __init__(self):
    """
    Initiate the object with the proper API keys.
    """
    self.key = APIKeys.MANDRILL_KEY
    self.url = APIKeys.MANDRILL_URL

  def send(self, email):
    """
    Send the email using the provided email dict.
    """
    data = {
              "key": self.key,
              "message": {
                "from_email": email['from'],
                "from_name":  email['from_name'],
                "to": [{
                  "email": email['to'],
                  "name":  email['to_name'],
                  "type": "to"
                }],
                "subject": email['subject'],
                "html": email['html'],
                "text": email['text'],
                "attachments": [{}]
              }
            }
    request = urllib2.Request(self.url,
                              json.dumps(data),
                              headers={'Content-Type': 'application/json'})
    handler = urllib2.urlopen(request)
    return handler.read()
