import os, time, requests

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

  def __get_data(self, email):
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

    return data

  def send(self, email):
    """
    Send the email using the provided Email object.
    """
    resp = requests.post(
        self.url,
        auth=('api', self.key),
        data=self.__get_data(email))
    return (resp.text, resp.status_code)
