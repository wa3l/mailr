import os, datetime, time, flask, requests

class Mandrill():
  """
  Wrapper for Mandrill

  Automatically handles creating a request to the Mandrill service
  provided a email object that contains email data.
  """
  key = os.environ['MANDRILL_KEY']
  url = os.environ['MANDRILL_URL']

  def send(self, email):
    """
    Send the email using the provided Email object.
    """
    resp = requests.post(
        self.url,
        data=self.__get_data(email),
        headers={'content-type': 'application/json'})
    return resp


  def __get_data(self, email):
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

    return flask.json.dumps(data)
