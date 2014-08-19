import os, flask
from helpers import *
from validation import Validator
from email_model import db
from flask.ext.sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
from flask.ext.httpauth import HTTPBasicAuth
from sqlalchemy.exc import DatabaseError

app  = flask.Flask(__name__)
auth = HTTPBasicAuth()
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db.app = app
db.init_app(app)

app.config['default'] = 'Mailgun'
app.config['backup']  = 'Mandrill'


"""
This is the main point of interaction with the app.
It accepts a json request to send an email. It sends
the email and stores its details in the database.
"""
@app.route('/email', methods=['POST'])
def email():
  # build email dict:
  data = json_data(flask.request)

  # validate data against schema
  valid, msg = Validator().validate(data)
  if not valid: return abort(msg)

  code   = 0
  backup = app.config['backup']

  # try the request, and retry upon failure.
  while code is not 200:
    resp, code = send_email(data, app.config)
    if code is 200: break
    log_error(app.logger, data, resp, code)
    if data['provider'] is backup:
      return abort('An error has occurred.', code)
    data['provider'] = backup

  # everything OK.
  store_email(db, data)
  return flask.jsonify(resp)


"""
Return a json object containing sent emails stored
in our database. The results are paginated and the
page size is fixed to 20 results.
"""
@app.route('/emails/', defaults={'page': 1})
@app.route('/emails/<int:page>', methods=['GET'])
@auth.login_required
def emails(page):
  email = Email.query.paginate(page, 20, False)
  resp   = {}
  for e in email.items:
    resp[e.id] = str(e)
  return flask.jsonify(page=page, emails=resp)


"""
Error and Basic Auth handling.
"""
@auth.get_password
def get_password(username):
  if username == 'api':
    return os.environ['MAILR_KEY']
  return None

@auth.error_handler
def unauthorized():
  return abort('Unauthorized access.', 401)

@app.errorhandler(DatabaseError)
def special_exception_handler(error):
  return abort('Database Error occurred.', 500)

@app.errorhandler(404)
def page_not_found(error):
  return abort('The requested URL was not found on the server.', 404)


if __name__ == '__main__':
  app.run(debug=True)

