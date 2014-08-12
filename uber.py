import os
from flask import Flask, request
from mailgun  import Mailgun
from mandrill import Mandrill
import html2text as convert
from validation import Validator

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def index():
  return "this is a test index page"


@app.route('/email', methods=['POST'])
def email():
  # build email dict:
  email_object = {
    "to":        request.form['to'],
    "to_name":   request.form['to_name'],
    "from":      request.form['from'],
    "from_name": request.form['from_name'],
    "subject":   request.form['subject'],
    "text":      convert.html2text(request.form['body']),
    "html":      request.form['body']
  }
  validator = Validator()
  result = validator.validate(email_object)
  if result != True: return str(result)
  m = Mailgun()
  # m = Mandrill()
  response = m.send(email_object)
  return response


if __name__ == '__main__':
  app.run()
