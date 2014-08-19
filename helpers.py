from flask import jsonify, json
import html2text as convert
import email_model

"""
Helper functions used in the app.
"""

def json_data(req):
  """(flask.request) -> dict
  Returns a dict representing the json request
  submitted to /email.
  """
  data = json.loads(req.get_json())
  return {k: v.strip() for k, v in data.iteritems()}


def email_service(service):
  """(str) -> Mailgun() or Mandrill()
  Returns a wrapper object of the default mail provider.
  """
  module  = __import__(service)
  Service = getattr(module, service.capitalize())
  return Service()


def abort(message, code=400):
  """(str, int) -> flask.Response
  Produces a response object with the proper error code and message.
  """
  resp = jsonify({'status': 'error', 'message': message})
  resp.status_code = code
  return resp


def log_error(logger, email, message, code):
  """(logger, str, str, int) -> None
  Logs an error: mention the mail provider
  name, the response message and code.
  """
  logger.error('Error {0} - {1} responded with: {2}'.format(code, email.provider, message))


def send_email(email, app):
  """(Email) -> (str, int)
  Processes the email body. Fires the correct email
  service and sends the email stored in data.
  Returns a response message and status code.
  """
  set_provider(email, app.config)
  service    = email_service(email.provider)
  resp, code = service.send(email)
  return (resp, code)


def set_provider(email, config):
  """(Email, dict) -> str
  Sets the correct email provider service.
  If user requested a specific provider then that
  is set as the default, otherwise, the app defaults
  are used.
  """
  if email.provider:
    config['default'] = email.provider.lower()
    if config['default'] == 'mailgun':
      config['backup'] = 'mandrill'
    else:
      config['backup'] = 'mailgun'
  email.provider = config['default']


def store_email(db, email):
  """(SQLAlchemy, Email) -> None
  Stores the email object in the database.
  """
  db.session.add(email)
  db.session.commit()
