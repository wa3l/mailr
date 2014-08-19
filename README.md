# Mailr is an app that wraps the Mailgun and Mandrill email services.
Mailr is a simple Python app written with Flask. It wraps [Mailgun](http://mailgun.com) and [Mandrill](http://mandrillapp.com), both email services that provide a RESTful API for sending/receiving emails. Flask is enough for the purposes of the project since it provides good routing other nifty features without adding much bloat to the application.

Mailr accepts POST requests with a JSON object at an `/email` endpoint. The request should have the parameters below:

```
- to: the email address to send to.
- to_name: the name to accompany the email.
- from: the email address to send from.
- from_name: the name to accompany the email.
- subject: the subject line.
- body: the HTML body of the email.
```
An example request payload:

```
{
"to": "batman@waynemansion.com",
"to_name": "Batman",
“from”: “alfred@waynemansion.com”,
"from_name": "Alfred",
"subject": "Robin emergency.",
"body": "<h1>Master Wayne,</h1><p>The Joker broke Robin's nose, again.</p>"
}
```

An example successful response is:

```
{
    "status": "success",
    "message": "Email queued to be sent by Mailgun."
}
```
Additionally, the app has an `/emails` endpoint that accepts a `page` parameter (as in `/emails/2` for instance). This endpoint requires Basic Auth with the username always being `api` and a password of your choosing. See the **Environment Variables** section for more on that.

##Installation
1. First, clone the repo: `git clone git@github.com:wa3l/mailr.git`

2. If you use [virtualenv](http://virtualenv.readthedocs.org/en/latest/), which it's recommended that you do, then go ahead and create a new environment `virtualenv venv` and activate it `source venv/bin/activate`. This will create a `venv` directory which contains a local environment with all the libraries that you need, as well as `pip` and a Python interpreter. The `venv` directory is included in `.gitignore`.

3. Now do `pip install -r requirements.txt` to install all the required libraries listed in `requirements.txt`.
4. You need PostgreSQL installed on your system. Refer to the official [website](http://www.postgresql.org) for instructions on how to install it. In my experience, [Postgres.app](http://postgresapp.com) is the most convenient way to install it on OS X. See the **Environment Variables** section for instructions on how to link a database to the code.

##Running

To run the app, you have two options.

1. By typing `python mailr.py`. **Note that you need to set your API keys in `.bashrc`**. See the **Environment Variables** section for more information.

2. By using [foreman](https://github.com/ddollar/foreman), a tool that lets you run multiple processes needed for your application using a `Procfile`. This is necessary for deploying the app on Heroku. In fact, foreman is installed by default when you install the [Heroku CLI tool](https://devcenter.heroku.com/categories/command-line), so this is a great way to have it installed. Once you have foreman installed, **you need to set up your API keys in a `.env` file**. See the **Environment Variables** section for more information.

    Now you can do `foreman start`
To start the app at `http://localhost:5000`.

Once you get the app running, you can start sending POST requests to `http://localhost:5000/email`.

###Notes:
1. You need to set your content-type to `application/json`, and don't forget to escape your double quotes in the JSON string.
2. You will need to quite foreman (`ctrl-C`) and do `foreman start` every time you make modifications to the code. Alternatively, you can get the best of both worlds by doing `foreman run python mailr.py`, which allows foreman to reload the code every time you make a change.


## Environment Variables
API keys are not kept in the git repository for obvious reasons. To set your own API keys, simply create a `.env` file in the main directory with the following content:

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
If you don't use foreman, then you can add your Mailgun API key, for instance, by adding this line to your `~/.bashrc`(or whatever file you use):

```
export MAILGUN_KEY=your_mailgun_api_key
```
Whichever way you endue using, you need to set all the API keys and URLs for both services. Additionally, you need to set the `DATABASE_URL` and `MAILR_KEY` variables. The first would probably be something like `postgresql://localhost/db_name` where `db_name` is a database you create for the app.

The other variable, `MAILR_KEY`, is any password you choose to access the `/emails` endpoint.

## Input validation
The required fields are: `to`, `to_name`, `from`, `from_name`, `subject` and `body`.
The `service` field is optional and only accepts the value `mailgun` or `mandrill`. It is otherwise ignored.

Similarly, the `deliverytime` field is also optional and accepts valid Unix timestamps between 0 and three days in the future. The three-day rule is requirement by Mailgun, so I opted to make it a requirement for both for simplicity. Additionally, Mandrill accepts a UTC timestamp in the `YYYY-MM-DD HH:MM:SS` format, but I chose to accept only Epoch timestamps to make the API uniform. Another solution would be to accept multiple date formats and convert them accordingly depending on the service used. This, however, makes validation more painful to manage. Please **note** that Mandrill does [not](http://help.mandrill.com/entries/24331201-Can-I-schedule-a-message-to-send-at-a-specific-time-) offer free delayed delivery emails, so you need to have a positive balance for this to work on Mandrill.

The `to` and `from` fields have to be valid email addresses. This is determined by scanning the given string against the following regex `"[\w\.\-]*@[\w\.\-\+]*\.\w+"`. Admittedly, this can be improved, but I chose to keep it simple for the purposes of this app. Regular expressions made for  email addresses can get pretty [nasty](http://www.ex-parrot.com/pdw/Mail-RFC822-Address.html). There are, however, limits on the minimum and maximum lengths of email addresses. I use 3 and [254](http://www.rfc-editor.org/errata_search.php?rfc=3696&eid=1690), respectively.

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

However, this behavior can be changed by modifying the `app.config['default']` and `app.config['backup']` configuration variables. Additionally, you can specify an email service in the JSON request using the `service` field. Setting this field takes precedence over the default settings.

Finally, regardless of the method you use to specify the preferred email service, the app will automatically determine if your preferred service is having issues/timeouts and will try the secondary service to send the email.

## Retrieving Emails
You need to access `/emails/page_number` to access the emails that pass through the app. This endpoint requires Basic Auth with the username being `api` and the password set in `.env`. It returns a JSON object that looks like this:

```
{
  "page": 1,
  "emails": {
    "1": "{'to': 'batman@waynemansion.com', 'to_name': 'Batman', 'from': 'alfred@waynemansion.com', 'from_name': 'Alfred', 'subject': 'Robin!', 'text': 'Robin is missing!', 'html': '<p>Robin is missing!</p>', 'service': 'Mailgun', 'deliverytime': '1408424058'}",
    "2": "{'to': 'alfred@waynemansion.com', 'to_name': 'Alfred', 'from': 'batman@waynemansion.com', 'from_name': 'Batman', 'subject': 're:Robin!', 'text': 'Good.', 'html': '<p>Good.</p>', 'service': 'Mailgun', 'deliverytime': '1408424058'}"
  }
}
```

## Things to do/improve
1. Test coverage. [Flask-Testing](https://pythonhosted.org/Flask-Testing/) looks like it would solve a lot of the limitations of testing under Flask.
2. ~~Check for the size of the body. Mailgun supports a [maximum](http://documentation.mailgun.com/user_manual.html#sending-via-api) message size of 25MB~~ Done.
3. ~~Perhaps use [Requests](http://docs.python-requests.org/en/latest/) to clean up the HTTP requests code.~~ Done. Working code that uses urllib2 can be seen in the commit history. Requests just simplifies the logic and makes code more readable.


## Author
Wael Al-Sallami | [about.me](http://about.me/wael).
