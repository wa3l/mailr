import urllib2, urllib, datetime
from urllib2  import HTTPError
from flask    import json

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

  def __get_json_object(self, data):
    """
    Build a json-encoded object to be sent to Mandrill.
    """
    email = {
      'key': self.key,
      'message': {
        'from_email': data['from'],
        'from_name':  data['from_name'],
        'to': [{
          'email': data['to'],
          'name':  data['to_name'],
          'type':  'to'
        }],
        'subject':  data['subject'],
        'html':     data['html'],
        'text':     data['text'],
        'attachments': [{}]
      }
    }
    if data.has_key('deliverytime'):
      # construct time in YYYY-MM-DD HH:MM:SS format.
      # Note: no need to worry about float() throwing
      # an exception, validation has already done that.
      timestamp        = float(data['deliverytime'])
      utc_datetime     = datetime.datetime.utcfromtimestamp(timestamp)
      email['send_at'] = utc_datetime.strftime('%Y-%m-%d %H:%M:%S')

    return json.dumps(email)


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
