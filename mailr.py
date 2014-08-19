import os, logging
from helpers import *
from validation import Validator
from email_model import Email
from email_model import db
from flask   import Flask, request, jsonify, json
from flask.ext.sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler


app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db.app = app
db.init_app(app)

app.config['default'] = 'Mailgun'
app.config['backup']  = 'Mandrill'

@app.route('/')
def home():
  return 'ha?'

@app.route('/email', methods=['POST'])
def email():
  # build email dict:
  data = json_data(request)

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

  # everything OK.
  return jsonify(resp)


if __name__ == '__main__':
  app.run()

