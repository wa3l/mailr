# Mailr is an app that wraps the Mailgun and Mandrill email services.
Mailr is a simple Python app written with Flask. It wraps [Mailgun](http://mailgun.com) and [Mandrill](http://mandrillapp.com), both email services that provide a RESTful API for sending/receiving emails. 
      
Mailr accepts a POST request with a JSON object at an `/email` endpoint. The request should have the parameters below:

```
- to: the email address to send to.
- to_name: the name to accompany the email.
- from: the email address to send from.
- from_name: the name to accompany the email.
- subject: the subject line.
- body: the HTML body of the email.
- provider: the name of an email provider.
```
An example request payload:

```
{
"to": "batman@waynemansion.com",
"to_name": "Batman",“from”: “alfred@waynemansion.com”, 
"from_name": "Alfred",
"subject": "Robin emergency.",
"body": "<h1>Master Wayne,</h1><p>The Joker broke Robin's nose, again.</p>",
"provider": "mailgun"}
```

An example successful response is:

```
{
    "status": "success",
    "message": "Email queued to be sent by Mailgun."
}
```

##Installation
1. First, clone the repo: `git clone git@github.com:wa3l/mailr.git`

2. If you use [virtualenv](http://virtualenv.readthedocs.org/en/latest/), which it's recommended that you do, then go ahead and create a new environment and activate it:

```
> virtualenv venv
> source venv/bin/activate
```
This will create a `venv` directory which contains a local environment with all the libraries that you need, as well as `pip` and a Python interpreter. The `venv` directory is included in `.gitignore`.

Now do: `pip install -r requirements.txt` to install all the required libraries listed in `requirements.txt`. 

##Running 

To run the app, you have two options. 

1. By typing `python mailr.py`. **Note that you need to set your API keys in `.bashrc`**. See the **API Keys** section for more information.

2. By using [foreman](https://github.com/ddollar/foreman), a tool that lets you run multiple processes needed for your application using a `Procfile`. This is necessary for deploying the app on Heroku. In fact, foreman is installed by default when you install the [Heroku CLI tool](https://devcenter.heroku.com/categories/command-line), so this is a great way to have it installed. Once you have foreman installed, **you need to set up your API keys in a `.env` file**. See the **API Keys** section for more information. 

    Now you can do `foreman start`
To start the app at `http://localhost:5000`. 

Once you get the app running, you can use send POST requests to `http://localhost:5000/email`.

###Notes:
1. You need to set your content-type to `application/json`, and don't forget to escape your double quotes in the JSON string.
2. You will need to to quite foreman (`ctrl-C`) and do `foreman start` every time you make modifications to the code. Alternatively, you can get the best of both worlds by doing `foreman run python mailr.py`, which allows foreman to reload the code every time you make a change.


## API Keys
API keys are not kept in the git repository for obvious reasons. To set your own API keys, simply create a `.env` file in the main directory using the following format:

```
MAILGUN_KEY  = your_mailgun_api_key
MAILGUN_URL  = your_mailgun_api_url
MANDRILL_KEY = your_mandrill_api_key
MANDRILL_URL = your_mandrill_api_url
```
foreman will make sure to load those environment variables when you startup the app. They are later accessed using `os.environ['VAR_NAME']`. This makes it easy to set those variables on multiple environments without conflicts. For instance, you can use the following command to set your Mailgun API key on Heroku:

```
heroku config:set MAILGUN_KEY=mailgun_api_key
```
Alternatively, you can add a variable to your `~/.bashrc` (or whatever file you use) like this: 

```export MAILGUN_KEY=your_mailgun_api_key```

## Input validation
The required fields are: `to`, `to_name`, `from`, `from_name`, `subject` and `body`.
The `provider` field is optional and only accepts the value `mailgun` or `mandrill`. It is otherwise ignored. 

Similarly, the `deliverytime` field is also optional and accepts valid Unix timestamps between 0 and three days in the future. The three-day rule is requirement by Mailgun, so I opted to make it a requirement for both for simplicity. Additionally, Mandrill accepts a UTC timestamp in the `YYYY-MM-DD HH:MM:SS` format, but I chose to accept only Epoch timestamps to make the API uniform. Another solution would be to accept multiple date formats and convert them accordingly depending on the service used. This, however, makes validation more painful to manage. Please **note** that Mandrill does [not](http://help.mandrill.com/entries/24331201-Can-I-schedule-a-message-to-send-at-a-specific-time-) offer free delayed delivery emails, so you need to have a positive balance for this to work on Mandrill.

The `to` and `from` fields have to be valid email addresses. This is determined by scanning the given string against the following regex `"[\w\.\-]*@[\w\.\-\+]*\.\w+"`. Admittedly, this can be improved, but I chose to keep it simple for the purposes of this app. Regular expressions made for  email addresses can get pretty [nasty](http://www.ex-parrot.com/pdw/Mail-RFC822-Address.html). There are, however, limits on the minimum and maximum lengths of email addresses. In this app, I use 3 and [254](http://www.rfc-editor.org/errata_search.php?rfc=3696&eid=1690)].

The subject line and body fields are required, and thus have a minimum length of 1 character. The subject line's maximum length is [78](http://www.faqs.org/rfcs/rfc2822.html). The body field has no upper limit on its size and is not checked for correct HTML syntax. 

If any of the above rules are not met in the provided JSON data, the app will respond with a `400 BAD REQUEST` and something along those lines:

```
{
    "status": "error",
    "message": "Invalid email address."
}
```

## Plaintext body
The app send an email with the provided HTML body. Additionally, it processes the provided HTML to produce a plaintext version and sends that along with the HTML. This is done via Aaron Swartz's [html2text](https://github.com/aaronsw/html2text) which happens to produces valid Markdown too!

## Sending emails
Mailgun is used as the default email service. Mandrill is used as backup. The decision is based on Mailgun's faster delivery, clearer documentation, and better error responses. Mandrill promises appropriate error codes/messages but have in my experience only responded with `500 Internal Error' headers for any kind of error.

However, this behavior can be changed by modifying the app.config['default'] and app.config['backup'] configuration variables. Additionally, you can specify a provider in the JSON request using the `provider` field. Setting this field takes precedence over the default settings. 

Finally, regardless of the method you use to specify the preferred email service, the app will automatically determine if your preferred service is having issues/timeouts and will try the secondary service to send the email.