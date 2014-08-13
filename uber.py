import os, helpers, logging
from flask import Flask, request, jsonify, json
from validation import Validator
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config['DEBUG']        = True
app.config['def_provider'] = 'Mailgun'
app.config['sec_provider'] = 'Mandrill'

@app.route('/email', methods=['POST'])
def email():
  # build email dict:
  data = helpers.json_data(request)

  # validate data against schema
  valid, msg = Validator().validate(data)
  if not valid: return helpers.bad_response(msg)

  # process body and send email
  data       = helpers.convert_body(data)
  provider   = app.config['def_provider']
  service    = helpers.email_service(provider)
  resp, code = service.send(data)

  # Any errors?
  if code is not 200:
    helpers.log_error(app.logger, provider, resp, code)
    msg = 'An error has occurred while sending the email.'
    return helpers.bad_response(msg, code)

  # everything OK.
  return jsonify(resp)


if __name__ == '__main__':
  app.run()

