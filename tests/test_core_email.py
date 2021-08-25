from unittest import mock

import pytest
from AuthX.core.email import EmailClient


@pytest.mark.asyncio
@pytest.mark.parametrize("language", ["EN"])
@mock.patch("aiosmtplib.send", mock.AsyncMock(return_value=None))
async def test_email_client(language: str):
    email_client = EmailClient(None, None, None, None, language, "", "", "")

    await email_client.send_confirmation_email("", "")
    await email_client.send_forgot_password_email("", "")
