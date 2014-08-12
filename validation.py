import re
from voluptuous import Schema, Required, All, Length, MultipleInvalid, Invalid

class Validator():
  """
  Validator class for POST input email data.
  """

  def __init__(self):
    """
    Define the validation schema
    """
    self.schema = Schema({
        'to':        All(self.validate_email, Length(min=6, max=254)),
        'from':      All(self.validate_email, Length(min=6, max=254)),
        'to_name':   All(unicode, Length(min=1)),
        'from_name': All(unicode, Length(min=1)),
        'subject':   All(unicode, Length(min=1, max=78)),
        'body':      All(unicode, Length(min=1))
    }, extra=True, required=True)


  def validate_email(self, email_address):
    """
    Validate an email address against a regex
    """
    if re.match("[\w\.\-]*@[\w\.\-\+]*\.\w+", email_address):
      return email_address
    else:
      raise Invalid("Invalid email address.")


  def validate(self, email):
    """
    Perform validation against the validation schema.
    """
    try:
      self.schema(email)
    except MultipleInvalid as e:
      return {'status': 'error', 'message': str(e)}
    return True
