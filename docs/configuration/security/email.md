# Email Configuration

Setup the email configuration for the application, this is the main
configuration for the email service.

Using the `EmailClient` We can use it to extend in the features of
`Sending Emails` and Confirmation emails.

```py
from authx import EmailClient

email_client = EmailClient(
    host='smtp.gmail.com',
    port=587,
    username='username',
    password='password',
    tls=True,
    display_name='AuthX',
    base_url='http://localhost:8000'
)
```

I provide also some functions that could help you while using authentication and
want to verify the email.
