import sys
import re, time
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
        'body':      All(self.validate_body, Length(min=1)),
        'to_name':   All(unicode, Length(min=1, max=256)),
        'from_name': All(unicode, Length(min=1, max=256)),
        'subject':   All(unicode, Length(min=1, max=78)),
        Optional('service'):     All(self.validate_service),
        Optional('deliverytime'): All(self.validate_time)
    }, extra=True, required=True)


  def validate_body(self, body):
    """
    Validate the body to be a unicode string
    that is <= 25MB in size (required by Mailgun).
    """
    if not isinstance(body, unicode):
      raise Invalid("Invalid body data type")

    size = sys.getsizeof(body)
    if size > 25 * 10**6:
      raise Invalid("Body is larger than 25MB")

    return body



  def validate_time(self, deliverytime):
    """
    Validate delivery time as a float an Epoch
    timestamp between the Epoch and 3 days in the future.
    """
    try:
      t = float(deliverytime)
    except ValueError as e:
      raise Invalid("Invalid Unix timestamp")

    # set max dat to 3 days from now.
    max_date = time.time() + 259200
    if not 0 <= t <= max_date:
      raise Invalid("Date negative or too far in the future")

    return t


  def validate_service(self, service):
    """
    Validate an email service name (either mailgun or mandrill).
    """
    if service.lower() in ['mandrill', 'mailgun']:
      return service
    else:
      raise Invalid("Invalid email service")


  def validate_email(self, email_address):
    """
    Validate an email address against a regex
    """
    if re.match("[\w\.\-]*@[\w\.\-\+]*\.\w+", email_address):
      return email_address
    else:
      raise Invalid("Invalid email address")


  def validate(self, data):
    """
    Perform validation against the validation schema.
    """
    try:
      self.schema(data)
    except MultipleInvalid as e:
      return (False, str(e))
    return (True, 'All data is valid.')
