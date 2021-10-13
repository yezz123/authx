# What's Next

After Providing some Ways of Social Authentication, we can also made this more strong by adding an email verification process, or a captcha to the login form.

## Captcha

CAPTCHAs are tools you can use to differentiate between real users and automated users, such as bots. CAPTCHAs provide challenges that are difficult for computers to perform but relatively easy for humans. For example, identifying stretched letters or numbers, or clicking in a specific area.

Using [httpx](https://www.python-httpx.org/) is a fully featured HTTP client for Python 3, which provides sync and async APIs, and support for both HTTP/1.1 and HTTP/2, this one gonna help us provide and validate Google Captcha.

!!! info
    This one Support only Google Captcha, but you can use any other captcha service, just make sure you have the correct API key, and also with same logical code.

### Validate Captcha

We use as an arguments `captcha` & `recaptcha_secret`, to get a boolean value, if the captcha is valid or not.

```py
from typing import Optional

from httpx import AsyncClient

async def validate_captcha(captcha: Optional[str], recaptcha_secret: str):
    if captcha is None:
        return False
    async with AsyncClient(base_url="https://www.google.com") as client:
        payload = {
            "secret": recaptcha_secret,
            "response": captcha,
        }
        response = await client.post("/recaptcha/api/siteverify", data=payload)
        response_obj = response.json()
        return response_obj.get("success")
```

!!! warning
    You could bypass this part cause its just an optional features for you to use.

## Check & Sign

This part relate to how we can generate or create a random string using [passlib](https://passlib.readthedocs.io/en/stable/index.html) a
a password hashing library for Python 2 & 3, which provides cross-platform implementations of over 30 password hashing algorithms.

```py
from passlib.pwd import genword

def create_random_string(length: int = 256) -> str:
    return genword(length=length)
```

Then we use [hashlib](https://docs.python.org/3/library/hashlib.html) to generate a hash value from the random string, and [hmac](https://docs.python.org/3/library/hmac.html) to generate a signature from the hash value.

All of this to sign & hash a string, then check the signature to make sure the string is not tampered with.

```py
import hashlib
import hmac

def sign_string(s: str, key: str) -> str:
    return hmac.new(key.encode(), s.encode(), hashlib.sha256).hexdigest()


def hash_string(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def check_signature(s: str, signature: str, key: str) -> bool:
    return signature == hmac.new(key.encode(), s.encode(), hashlib.sha256).hexdigest()
```
