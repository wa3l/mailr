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

@app.route('/email', methods=['POST'])
def email():
  # build email dict:
  email = {}
  for k, v in request.form.items():
    email[k] = v.strip()

  result = Validator().validate(email)
  if result != True:
    return json.dumps(result)

  process_body(email)

  service    = email_service()
  resp, code = service.send(email)
  if code != 200:
    app.logger.error('Error {0} - {1} responded with: {2}'.format(code, app.config['default_service'], resp))
    return json.dumps({
                      'status':  'error',
                      'message': 'An error has occurred on the email service provider\'s end.'
                      })

  return json.dumps(resp)


if __name__ == '__main__':
  app.run()
