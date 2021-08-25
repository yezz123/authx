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
