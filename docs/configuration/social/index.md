# Social Authentication

**AuthX** Allows you to plug in several social authentication providers.

## How its Works?

Social Login is single sign-on for end users. Using existing login information from a social network provider like Facebook, Twitter, or Google, the user can sign into a third party website instead of creating a new account specifically for that website.

At AuthX, After we create the Social [Models](../models/social.md), We can generate a social Login, based on a preconfigured services, using `httpx` an asynchronous HTTP client.

For Now, we have only two social providers:

* [Facebook](facebook.md)
* [google](google.md)

Also, an [Addons](addons.md) is available to add some utility functions to the social login, for example captcha, email verification, etc.

```py
from authx import Authentication
from fastapi import FastAPI

auth = Authentication()

app = FastAPI()

app.include_router(auth.social_router, prefix="/auth")
```
