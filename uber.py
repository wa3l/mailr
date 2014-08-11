import os
from flask import Flask
from flask import request

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def index():
  return "this is a test index page"


@app.route('/email', methods=['GET', 'POST'])
def email():
  assert request.method == 'POST'
  # this is a test email page
  return request.form['body']


if __name__ == '__main__':
  app.run()

