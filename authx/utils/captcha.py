from typing import Optional

from httpx import AsyncClient


async def validate_captcha(captcha: Optional[str], recaptcha_secret: str):
    """
    Validate a captcha.

    Args:
        captcha (Optional[str]): The captcha to validate.
        recaptcha_secret (str): The recaptcha secret.

    Returns:
        bool: Whether the captcha is valid.
    """
    if captcha is None:
        # TODO: Log this
        return False
    async with AsyncClient(base_url="https://www.google.com") as client:
        """
        The Google API for validating a captcha.

        Returns:
            bool: Whether the captcha is valid.
        """
        payload = {
            "secret": recaptcha_secret,
            "response": captcha,
        }
        # TODO: Log this
        response = await client.post("/recaptcha/api/siteverify", data=payload)
        response_obj = response.json()
        return response_obj.get("success")
