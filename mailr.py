import os, flask
from helpers import *
from validation import Validator
from email_model import Email, db
from flask.ext.sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
from flask.ext.httpauth import HTTPBasicAuth
from sqlalchemy.exc import DatabaseError

app  = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db.app = app
db.init_app(app)

app.config['default'] = 'Mailgun'
app.config['backup']  = 'Mandrill'

auth = HTTPBasicAuth()


@app.route('/email', methods=['POST'])
def email():
  # build email dict:
  data = json_data(flask.request)

  # validate data against schema
  valid, msg = Validator().validate(data)
  if not valid:
    return bad_response(msg)

  # send email
  set_provider(data, app.config)
  resp, code = send_email(data)

  # Retry with backup provider if there are errors
  if code is not 200:
    log_error(app.logger, data['provider'], resp, code)
    data['provider'] = app.config['backup']
    resp, code       = send_email(data)

  # Still no success?
  if code is not 200:
    log_error(app.logger, provider, resp, code)
    msg = 'An error has occurred while sending the email.'
    return bad_response(msg, code)

  e = Email(data)
  db.session.add(e)
  db.session.commit()
  # everything OK.
  return flask.jsonify(resp)


@app.route('/emails/', defaults={'page': 1})
@app.route('/emails/<int:page>', methods=['GET'])
@auth.login_required
def emails(page):
  email = Email.query.paginate(page, 20, False)
  resp   = {}
  for e in email.items:
    resp[e.id] = str(e)
  return flask.jsonify(page=page, emails=resp)


@auth.get_password
def get_password(username):
  if username == 'api':
    return os.environ['MAILR_API_KEY']
  return None

@auth.error_handler
def unauthorized():
  return bad_response('Unauthorized access.', 401)

@app.errorhandler(DatabaseError)
def special_exception_handler(error):
  return bad_response('Database Error occurred.', 500)

@app.errorhandler(404)
def page_not_found(error):
  return bad_response('The requested URL was not found on the server.', 404)


if __name__ == '__main__':
  app.run(debug=True)

