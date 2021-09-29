from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator

from AuthX.models.common import set_created_at, set_last_login


class SocialInCreate(BaseModel):
    """
    SocialInCreate is a model for the input of the Social model.

    Args:
        email (str): The email of the user.
        password (str): The password of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        created_at (datetime): The date and time the user was created.
        last_login (datetime): The date and time the user last logged in.
    """

    email: EmailStr
    username: str
    provider: str
    sid: str
    active: bool = True
    confirmed: bool = True
    permissions: list = []
    info: list = []
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    _created_at = validator("created_at", pre=True, always=True, allow_reuse=True)(
        set_created_at
    )
    _last_login = validator("last_login", pre=True, always=True, allow_reuse=True)(
        set_last_login
    )
