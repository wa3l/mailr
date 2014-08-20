from flask import jsonify, json

"""
Helper functions used in the app.
"""

def json_data(req):
  """(flask.request) -> dict
  Returns a dict representing the json request
  submitted to /email.
  """
  return {k: v.strip() for k, v in req.get_json().iteritems()}


def get_services(email, app):
  """(Email) -> list
  Return a tuple containing email service names in order
  """
  services = app.config['SERVICES'][:]
  if email.service == 'mandrill':
    services.reverse()
  return services


def abort(message, code=400):
  """(str, int) -> flask.Response
  Produces a response object with the proper error code and message.
  """
  resp = jsonify({'status': 'error', 'message': message})
  resp.status_code = code
  return resp


def success(email):
  """(Email) -> flask.Response
  Produces a response object with a success message.
  """
  return jsonify({
    'status':  'success',
    'message': 'Email queued to be sent by {}.'.format(email.service.capitalize())
  })


def log_error(logger, email, resp):
  """(logger, Email, requests.Request) -> None
  Logs an error: mention the mail service
  name, the response message and code.
  """
  logger.error('Error {0} - {1} responded with: {2}'.format(resp.status_code, email.service, resp.text))


def send_email(email):
  """(Email) -> (str, int)
  Processes the email body. Fires the correct email
  service and sends the email stored in data.
  Returns a response message and status code.
  """
  service = service_obj(email.service)
  return service.send(email)


def service_obj(service):
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
