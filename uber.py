import os, json
import html2text as convert
from   flask      import Flask, request, jsonify
from   validation import Validator
import logging
from   logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['default_service'] = 'Mailgun'
app.config['backup_service']  = 'Mandrill'


def email_service():
  name    = app.config['default_service']
  module  = __import__(name.lower())
  Service = getattr(module, name)
  return Service()


def process_email_body(email):
  email['html'] = email['body']
  email['text'] = convert.html2text(email['body'])
  email.pop('body')


def bad_response(message, code=400):
  resp = jsonify({'status': 'error', 'message': message})
  resp.status_code = code
  return resp


@app.route('/email', methods=['POST'])
def email():
  # build email dict:
  data = json.loads(request.get_json(force=True))
  data = {k: v.strip() for k, v in data.iteritems()}

  (valid, msg) = Validator().validate(data)
  if not valid: return bad_response(msg)

  process_email_body(data)
  service    = email_service()
  resp, code = service.send(data)

  # Any errors?
  if code is not 200:
    app.logger.error('Error {0} - {1} responded with: {2}'.format(code, app.config['default_service'], resp))
    message = 'An error has occurred while sending the email.'
    return bad_response(message, code)

  # everything OK.
  return jsonify(resp)


if __name__ == '__main__':
  app.run()

