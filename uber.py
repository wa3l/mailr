import os, json
import html2text as convert
from   flask      import Flask, request
from   mailgun    import Mailgun
from   mandrill   import Mandrill
from   validation import Validator

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def index():
  return "this is a test index page"


@app.route('/email', methods=['POST'])
def email():
  # build email dict:
  validator = Validator()

  email = {}
  for k, v in request.form.items():
    email[k] = v.strip()

  result = validator.validate(email)
  if not result == True: return str(result)

  email['html'] = email['body']
  email['text'] = convert.html2text(email['body'])
  # email.pop('body')

  m       = Mailgun()
  # m       = Mandrill()
  response  = m.send(email)
  return response


if __name__ == '__main__':
  app.run()
