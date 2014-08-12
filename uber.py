import os
from flask import Flask, request
from mailgun  import Mailgun
from mandrill import Mandrill
import html2text as convert

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def index():
  return "this is a test index page"


@app.route('/email', methods=['GET', 'POST'])
def email():
  # test email service:
  html = "<h1>Your Bill</h1><p>$10</p>"
  email = {
    "to": "walsallami@gmail.com",
    "to_name": "Wael Al-Sallami",
    "from": "wael.alsallami@gmail.com",
    "from_name": "Katie Lea",
    "subject": "A Message from Uber",
    "text": convert.html2text(html),
    "html": html
  }
  m = Mailgun()
  # m = Mandrill()
  response = m.send(email)
  return response


if __name__ == '__main__':
  app.run()
