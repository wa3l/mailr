from api_keys import APIKeys
import urllib2, urllib, json
from urllib2 import HTTPError

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
    data = json.dumps({
              "key": self.key,
              "message": {
                "from_email": email['from'],
                "from_name":  email['from_name'],
                "to": [{
                  "email":  email['to'],
                  "name":   email['to_name'],
                  "type":   "to"
                }],
                "subject":  email['subject'],
                "html":     email['html'],
                "text":     email['text'],
                "attachments": [{}]
              }
            })
    header  = {'Content-Type': 'application/json'}
    request = urllib2.Request(self.url, data, headers=header)
    # Note: Mandrill appears to be responding with 500 error code for any error.
    try:
      handler = urllib2.urlopen(request)
    except HTTPError as e:
      return (e.reason, e.code)

    response = {
                'status':  'success',
                'message': 'Email queued to be sent by Mandrill.'
                }
    return (response, handler.getcode())
