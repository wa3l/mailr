import os, flask
from helpers import *
from validation import Validator
from email_model import db, Email
from flask.ext.httpauth import HTTPBasicAuth
from sqlalchemy.exc import DatabaseError
from os import environ

app  = flask.Flask(__name__)
auth = HTTPBasicAuth()
env  = environ['MAILR_ENV'] if environ.has_key('MAILR_ENV') else 'Development'
app.config.from_object('config.{}Config'.format(env))
db.app = app
db.init_app(app)

"""
This is the main point of interaction with the app.
It accepts a json request to send an email. It sends
the email and stores its details in the database.
"""
@app.route('/email', methods=['POST'])
def email():
  data       = json_data(flask.request)
  valid, msg = Validator().validate(data)
  if not valid: return abort(msg)

  email = Email(data)

  for s in get_services(email, app):
    email.service = s
    resp = send_email(email)
    if resp.status_code is 200:
      save_email(db, email)
      return success(email)
    else:
      log_error(app.logger, email, resp)

  return abort('An error has occurred.', resp.status_code)


"""
Return a json object containing sent emails stored
in our database. The results are paginated and the
page size is fixed to 20 results.
"""
@app.route('/emails/', defaults={'page': 1})
@app.route('/emails/<int:page>', methods=['GET'])
@auth.login_required
def emails(page):
  emails = Email.query.paginate(page, 20, False)
  resp   = {e.id: str(e) for e in emails.items}
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

@app.errorhandler(400)
def page_not_found(error):
  return abort('Invalid JSON request.', 400)


if __name__ == '__main__':
  app.run()
  db.create_all()
