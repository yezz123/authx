from typing import TYPE_CHECKING, Any, Dict, Generic, Optional

from fastapi import Request, Response

from authx.types import DateTimeExpression, StringOrSequence, T

if TYPE_CHECKING:
    from authx.main import AuthX


class AuthXDependency(Generic[T]):
    def __init__(
        self,
        _from: "AuthX[T]",
        request: Request,
        response: Response,
    ) -> None:
        self._response = response
        self._request = request
        self._security = _from

    @property
    def request(self):
        return self._request

    @property
    def response(self):
        return self._response

    def create_access_token(
        self,
        uid: str,
        fresh: bool = False,
        headers: Optional[Dict[str, Any]] = None,
        expiry: Optional[DateTimeExpression] = None,
        data: Optional[Dict[str, Any]] = None,
        audience: Optional[StringOrSequence] = None,
        *args,
        **kwargs,
    ) -> str:
        return self._security.create_access_token(
            uid, fresh, headers, expiry, data, audience, *args, **kwargs
        )

    def create_refresh_token(
        self,
        uid: str,
        headers: Optional[Dict[str, Any]] = None,
        expiry: Optional[DateTimeExpression] = None,
        data: Optional[Dict[str, Any]] = None,
        audience: Optional[StringOrSequence] = None,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        return self._security.create_refresh_token(
            uid, headers, expiry, data, audience, *args, **kwargs
        )

    def set_access_cookies(
        self, token, response: Optional[Response] = None, max_age: Optional[int] = None
    ):
        self._security.set_access_cookies(
            token=token, response=(response or self._response), max_age=max_age
        )

    def set_refresh_cookies(
        self, token, response: Optional[Response] = None, max_age: Optional[int] = None
    ):
        self._security.set_refresh_cookies(
            token=token, response=(response or self._response), max_age=max_age
        )

    def unset_access_cookies(self, response: Optional[Response] = None):
        self._security.unset_access_cookies(response=(response or self._response))

    def unset_refresh_cookies(self, response: Optional[Response] = None):
        self._security.unset_access_cookies(response=(response or self._response))

    def unset_cookies(self, response: Optional[Response] = None):
        self._security.unset_cookies(response=(response or self._response))

    async def get_current_subject(self) -> Optional[T]:
        return await self._security.get_current_subject(request=self._request)
