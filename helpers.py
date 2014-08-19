from flask import jsonify, json

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


def abort(message, code=400):
  """(str, int) -> flask.Response
  Produces a response object with the proper error code and message.
  """
  resp = jsonify({'status': 'error', 'message': message})
  resp.status_code = code
  return resp


def log_error(logger, service, message, code):
  """(logger, str, str, int) -> None
  Logs an error: mention the mail service
  name, the response message and code.
  """
  logger.error('Error {0} - {1} responded with: {2}'.format(code, service, message))


def send_email(email):
  """(Email) -> (str, int)
  Processes the email body. Fires the correct email
  service and sends the email stored in data.
  Returns a response message and status code.
  """
  service    = email_service(email.service)
  resp, code = service.send(email)
  return (resp, code)


def email_service(service):
  """(str) -> Mailgun() or Mandrill()
  Returns a wrapper object of the default email service.
  """
  module  = __import__(service)
  Service = getattr(module, service.capitalize())
  return Service()


def save_email(db, email):
  """(SQLAlchemy, Email) -> None
  Saves the email object in the database.
  """
  db.session.add(email)
  db.session.commit()
