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
  module  = __import__(service.lower())
  Service = getattr(module, service)
  return Service()


def convert_body(data):
  """(dict) -> dict
  Moves the email body to data['html'], converts that to Markdown
  and stores it in data['key'], then deletes data['body']
  """
  if data.has_key('body'):
    data['html'] = data['body']
    data['text'] = convert.html2text(data['body'])
    data.pop('body')
  return data


def abort(message, code=400):
  """(str, int) -> flask.Response
  Produces a response object with the proper error code and message.
  """
  resp = jsonify({'status': 'error', 'message': message})
  resp.status_code = code
  return resp


def log_error(logger, data, message, code):
  """(logger, str, str, int) -> None
  Logs an error: mention the mail provider
  name, the response message and code.
  """
  logger.error('Error {0} - {1} responded with: {2}'.format(code, data['provider'], message))


def send_email(data, config):
  """(dict) -> (str, int)
  Processes the email body. Fires the correct email
  service and sends the email stored in data.
  Returns a response message and status code.
  """
  set_provider(data, config)
  data       = convert_body(data)
  service    = email_service(data['provider'])
  resp, code = service.send(data)
  return (resp, code)


def set_provider(data, config):
  """(dict, dict) -> str
  Sets the correct email provider service.
  If user requested a specific provider then that
  is set as the default, otherwise, the app defaults
  are used.
  """
  if data.has_key('provider'):
    config['default'] = data['provider'].capitalize()
    if config['default'].lower() == 'mailgun':
      config['backup'] = 'Mandrill'
    else:
      config['backup'] = 'Mailgun'
  data['provider'] = config['default']


def store_email(db, data):
  """(SQLAlchemy, dict) -> None
  Stores the email object in the database.
  """
  e = email_model.Email(data)
  db.session.add(e)
  db.session.commit()
