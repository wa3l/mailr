# Mailr is a wrapper around Mailgun and Mandrill.
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

## Installation


## Input validation
All fields are required except for `provider`. This field only accepts the value `mailgun` or `mandrill`, and is otherwise ignored. 

The `to` and `from` fields have to be valid email addresses. This is determined by scanning the given string against the following regex `"[\w\.\-]*@[\w\.\-\+]*\.\w+"`. Admittedly, this can be improved, but I chose to keep it simple for the purposes of this app. Regular expressions made for  email addresses can get pretty [nasty](http://www.ex-parrot.com/pdw/Mail-RFC822-Address.html). There are, however, limits on the minimum and maximum lengths of email addresses. In this app, I use 3 and 254[[1](http://www.rfc-editor.org/errata_search.php?rfc=3696&eid=1690)].

The subject line and body fields are required, and thus have a minimum length of 1 character. The subject line's maximum length is 78[[2](http://www.faqs.org/rfcs/rfc2822.html)]. The body field has no upper limit on its size and is not checked for correct HTML syntax. 

If any of the above rules are not met in the provided JSON data, the app will respond with a `400 BAD REQUEST` and something along those lines:

```
{
    "status": "error",
    "message": "Invalid email address."
}
```

## Plaintext body
The app send an email with the provided HTML body. Additionally, it processes the provided HTML to produce a plaintext version and send that along with it. This is done via Aaron Swartz's [html2text](https://github.com/aaronsw/html2text) which happens to produces valid Markdown.

## Sending emails
Mailgun is used as the default email service. Mandrill is used as backup. The decision is based on Mailgun's faster delivery, clearer documentation, and better error responses. However, it can be changed by modifying the app.config['default'] and app.config['backup'] configuration variables. Additionally, one can specify a provider in the JSON request, which takes precedence over the default settings. 

Finally, regardless of the method that was used to specify the preferred email service, the app will automatically determine if your preferred service is having issues and will try the secondary service to send the email.

## More Details