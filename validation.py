import re
from voluptuous import Schema, Optional, All, Length, MultipleInvalid, Invalid

class Validator():
  """
  Validator class for POST input email data.
  """

  def __init__(self):
    """
    Define the validation schema
    """
    self.schema = Schema({
        'to':        All(self.validate_email, Length(min=3, max=254)),
        'from':      All(self.validate_email, Length(min=3, max=254)),
        'to_name':   All(unicode, Length(min=1)),
        'from_name': All(unicode, Length(min=1)),
        'subject':   All(unicode, Length(min=1, max=78)),
        'body':      All(unicode, Length(min=1)),
        Optional('provider'): All(self.validate_provider)
    }, extra=True, required=True)


  def validate_provider(self, provider):
    """
    Validate an email provider (either Mailgun or Mandrill).
    """
    if provider.lower() in ['mandrill', 'mailgun']:
      return provider
    else:
      raise Invalid("Invalid email provider.")


  def validate_email(self, email_address):
    """
    Validate an email address against a regex
    """
    if re.match("[\w\.\-]*@[\w\.\-\+]*\.\w+", email_address):
      return email_address
    else:
      raise Invalid("Invalid email address.")


  def validate(self, data):
    """
    Perform validation against the validation schema.
    """
    try:
      self.schema(data)
    except MultipleInvalid as e:
      return (False, str(e))
    return (True, 'All data is valid.')
