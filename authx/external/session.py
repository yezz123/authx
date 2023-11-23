import uuid
from http.cookies import SimpleCookie

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from authx._internal import MemoryIO, SignatureSerializer


class SessionIntegration:
    def __init__(self, store, session_id, session_save):
        self.session_store = store
        self.session_id = session_id
        self.session_save = session_save

    def get_session(self):
        """Get the session store."""
        return self.session_store

    def clear_session(self):
        """Clear the session store."""
        self.session_store.clear()

    def get_session_id(self):
        """Get the session ID."""
        return self.session_id

    def save_session(self):
        """Save the session store."""
        self.session_save()


class SessionMiddleware(BaseHTTPMiddleware):
    """
    A FastAPI middleware for managing user sessions.
    """

    def __init__(
        self,
        app,
        secret_key,
        store=MemoryIO(),
        http_only=True,
        secure=True,
        max_age=0,
        session_cookie="sid",
        session_object="session",
        skip_session_header=None,
        logger=None,
    ):
        super().__init__(app)

        self.skip_session_header = skip_session_header
        self.http_only = http_only
        self.max_age = max_age
        self.secure = secure
        self.secret_key = secret_key
        self.session_cookie_name = session_cookie
        self.session_store = store
        self.serializer = SignatureSerializer(self.secret_key, expired_in=self.max_age)
        self.session_object = session_object
        self.logger = logger

        if self.logger is None:

            class ConsoleLogger:
                def info(self, str):
                    pass

                def debug(self, str):
                    pass

            self.logger = ConsoleLogger()

        self.logger.debug(
            f"Session Middleware initialized http_only:{http_only} secure:{secure} session_key:'{session_object}' session_cookie_name:{session_cookie} store:{store}"
        )

    def create_session_cookie(self, session_id):
        """
        Create and sign a session cookie.

        Args:
            session_id (str): The session ID.

        Returns:
            SimpleCookie: The signed session cookie.
        """
        session_id_dict_obj = {self.session_cookie_name: session_id}
        signed_session_id = self.serializer.encode(session_id_dict_obj)

        cookie = SimpleCookie()
        cookie[self.session_cookie_name] = signed_session_id

        self.logger.debug(
            f"[session_id:'{session_id}'] Creating new Cookie object... cookie[{self.session_cookie_name}]"
        )

        if self.http_only:
            self.logger.debug(f"[session_id:'{session_id}'] cookie[{self.session_cookie_name}]['httponly'] enabled")
            cookie[self.session_cookie_name]["httponly"] = True

        if self.secure:
            self.logger.debug(f"[session_id:'{session_id}'] cookie[{self.session_cookie_name}]['secure'] enabled")
            cookie[self.session_cookie_name]["secure"] = True

        if self.max_age > 0:
            self.logger.debug(
                f"[session_id:'{session_id}'] cookie[{self.session_cookie_name}]['maxage']={self.max_age} enabled"
            )
            cookie[self.session_cookie_name]["max-age"] = self.max_age

        return cookie

    def skip_session_header_check(self, request: Request) -> bool:
        """
        Check if session management should be skipped based on the request header.

        Args:
            request (Request): The incoming request.

        Returns:
            bool: True if session management should be skipped, False otherwise.
        """
        skip_header = self.skip_session_header

        if skip_header is None:
            self.logger.debug("Do not use skip_header option.")
            return False

        if isinstance(skip_header, dict):
            skip_header = [skip_header]

        header_names = []

        for header in skip_header:
            header_name = header.get("header_name")
            header_value = header.get("header_value")
            header_names.append(header_name)

            self.logger.debug(f"Use skip_header option. skip_header:'{header_name}':'{header_value}'")
            request_header_value = request.headers.get(header_name)
            self.logger.debug(
                f"Use skip_header option. Checking request header: '{header_name}':'{request_header_value}'"
            )
            if (header_value == "*" and request_header_value is not None) or request_header_value == header_value:
                self.logger.debug("Use skip_header option. skip_header matched!")
                return True

        self.logger.debug(f"Use skip_header option. skip_headers:{header_names} not matched in request headers.")
        return False

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Dispatch the request, handling session management.

        Args:
            request (Request): The incoming request.
            call_next (RequestResponseEndpoint): The next request handler.

        Returns:
            Response: The response from the request handler.
        """
        if self.skip_session_header_check(request):
            self.logger.debug("Skip session management.")
            return await call_next(request)

        signed_session_id = request.cookies.get(self.session_cookie_name)
        cookie = None

        if signed_session_id is None:
            self.logger.info("Completely new access with no session cookies")
            cookie = await self.create_new_session_id_and_store(request, cause="new")
        else:
            decoded_dict, err = self.serializer.decode(signed_session_id)

            if decoded_dict is not None:
                self.logger.debug("Cookie signature validation success")
                session_id = decoded_dict.get(self.session_cookie_name)
                session_store = self.session_store.get_store(session_id)

                if session_store is None:
                    self.logger.info(
                        f"[session_id:'{session_id}'] Session cookie available. But no store for this sessionId found. Maybe store had cleaned."
                    )
                    cookie = await self.create_new_session_id_and_store(request, cause="valid_cookie_but_no_store")
                else:
                    self.logger.info(
                        f"[session_id:'{session_id}'] Session cookie and Store is available! set session_mgr to reqeust.state.{self.session_object}"
                    )

                    setattr(
                        request.state,
                        self.session_object,
                        SessionIntegration(
                            store=session_store,
                            session_id=session_id,
                            session_save=lambda: self.session_store.save_store(session_id),
                        ),
                    )

                    session_store["__cause__"] = "success"

            else:
                self.logger.info(f"Session cookies available but verification failed! err:{err}")
                cookie = await self.create_new_session_id_and_store(request, cause=f"renew after {err}")

        response = await call_next(request)

        if cookie is not None:
            cookie_val = cookie.output(header="").strip()
            self.logger.info("Set response header 'Set-Cookie' to signed cookie value")
            response.headers["Set-Cookie"] = cookie_val

        return response

    async def create_new_session_id_and_store(self, request, cause=None):
        """
        Create a new session ID and its corresponding store.

        Args:
            request: The incoming request.
            cause (str): The cause of creating a new session ID.

        Returns:
            SimpleCookie: The signed session cookie.
        """
        session_id = str(uuid.uuid4())
        session_store = self.session_store.create_store(session_id)
        self.logger.debug(f"[session_id:'{session_id}'(NEW)] New session_id and store for session_id created.")

        if cause is not None:
            session_store["__cause__"] = cause

        fast_session_obj = SessionIntegration(
            store=session_store, session_id=session_id, session_save=lambda: self.session_store.save_store(session_id)
        )
        self.logger.info(f"[session_id:'{session_id}'(NEW)] Set session_mgr to request.state.{self.session_object} ")
        setattr(request.state, self.session_object, fast_session_obj)

        self.session_store.gc()

        return self.create_session_cookie(session_id)
