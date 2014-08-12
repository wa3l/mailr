import os, json
import html2text as convert
from   flask      import Flask, request
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

def process_body(email):
  email['html'] = email['body']
  email['text'] = convert.html2text(email['body'])
  email.pop('body')

@app.route('/')
def index():
  return "this is a test index page"


@app.route('/email', methods=['POST'])
def email():
  # build email dict:


  email = {}
  for k, v in request.form.items():
    email[k] = v.strip()

  result = Validator().validate(email)
  if result != True:
    return str(result)

  process_body(email)

  service    = email_service()
  resp, code = service.send(email)
  if code == 200:
    return str(resp)
  else:
    app.logger.error('Error {0} - Mailgun responded with: {1}'.format(code, resp))
    return {'status': 'error', 'message': "An error has occurred on the email service provider's end."}


if __name__ == '__main__':
  app.run()
