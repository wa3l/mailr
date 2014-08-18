import os, logging
from flask import Flask, request, jsonify, json
from validation import Validator
from logging.handlers import RotatingFileHandler
from helpers import *

app = Flask(__name__)
app.config['DEBUG']   = True
app.config['default'] = 'Mailgun'
app.config['backup']  = 'Mandrill'

@app.route('/email', methods=['POST'])
def email():
  # build email dict:
  data = json_data(request)

  # validate data against schema
  valid, msg = Validator().validate(data)
  if not valid:
    return bad_response(msg)

  # send email
  provider   = choose_provider(data, app.config)
  resp, code = send_email(data, provider)

  # Retry with backup provider if there are errors
  if code is not 200:
    log_error(app.logger, provider, resp, code)
    provider   = app.config['backup']
    resp, code = send_email(data, provider)

  # Still no success?
  if code is not 200:
    log_error(app.logger, provider, resp, code)
    msg = 'An error has occurred while sending the email.'
    return bad_response(msg, code)

  # everything OK.
  return jsonify(resp)


if __name__ == '__main__':
  app.run()

