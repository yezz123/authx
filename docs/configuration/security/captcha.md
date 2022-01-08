# Captcha

CAPTCHA (Completely Automated Public Turing test to tell Computers and Humans Apart) is a type of security measure known as challenge-response authentication.

Using `HTTPX` we can easily send a captcha to the user and verify it.

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
