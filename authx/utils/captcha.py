from typing import Optional

from httpx import AsyncClient


async def validate_captcha(captcha: Optional[str], recaptcha_secret: str):
    """Validate a captcha an Asynchrounous Captcha Validator based on the
    HTTPX AsyncClient, thats give us the ability to make requests to the
    Google Recaptcha API.
    """
    if captcha is None:
        # TODO: If there is a possibility of a captcha being required.
        return False
    async with AsyncClient(base_url="https://www.google.com") as client:
        payload = {
            "secret": recaptcha_secret,
            "response": captcha,
        }
        response = await client.post("/recaptcha/api/siteverify", data=payload)
        response_obj = response.json()
        return response_obj.get("success")
