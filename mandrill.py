from api_keys import APIKeys
import urllib2, urllib, json
from urllib2 import HTTPError

class Mandrill():
  """
  Wrapper for Mandrill

  Automatically handles creating a request to the Mandrill service
  provided a email object that contains email data.
  """
  key = APIKeys.MANDRILL_KEY
  url = APIKeys.MANDRILL_URL
  success = {
    'status':  'success',
    'message': 'Email queued to be sent by Mandrill.'
  }

  def __get_json_object(self, data):
    return json.dumps({
      "key": self.key,
      "message": {
        "from_email": data['from'],
        "from_name":  data['from_name'],
        "to": [{
          "email": data['to'],
          "name":  data['to_name'],
          "type":  "to"
        }],
        "subject":  data['subject'],
        "html":     data['html'],
        "text":     data['text'],
        "attachments": [{}]
      }
    })


  def send(self, data):
    """
    Send the email using the provided email dict.
    """
    data    = self.__get_json_object(data)
    header  = {'Content-Type': 'application/json'}
    request = urllib2.Request(self.url, data, headers=header)
    # Note: Mandrill appears to be responding with 500 error code for any error.
    try:
      handler = urllib2.urlopen(request)
    except HTTPError as e:
      return (e.reason, e.code)

    return (self.success, handler.getcode())
