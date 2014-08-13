import html2text as convert
from flask import jsonify, json

"""
Helper functions used in the app.
"""

def json_data(req):
  data = json.loads(req.get_json())
  return {k: v.strip() for k, v in data.iteritems()}


def email_service(service):
  """
  Returns a wrapper object of the default mail provider.
  """
  module  = __import__(service.lower())
  Service = getattr(module, service)
  return Service()


def convert_body(data):
  """
  Moves the email body to data['html'], converts that to Markdown
  and stores it in data['key'], then deletes data['body']
  """
  data['html'] = data['body']
  data['text'] = convert.html2text(data['body'])
  data.pop('body')
  return data


def bad_response(message, code=400):
  """
  Produces a response object with the proper error code and message.
  """
  resp = jsonify({'status': 'error', 'message': message})
  resp.status_code = code
  return resp

def log_error(logger, provider, message, code):
  """
  Log an error: mention the mail provider name
  and the response message and code.
  """
  logger.error('Error {0} - {1} responded with: {2}'.format(code, provider, message))
