# Session Middleware

The Session Middleware is a powerful tool that enables efficient management of user sessions in FastAPI applications.

## Features

The Session Middleware offers the following features:

### 1. Session ID Management

The middleware generates a unique session ID for each user session. This session ID is stored as a browser cookie. This approach is similar to how session management is handled in Java Servlet and Node.js Express frameworks.

### 2. Enhanced Security

The session ID is the only piece of information stored in the browser cookie. By avoiding the storage of session contents in the browser, the Session Middleware allows for the creation of an exceptionally secure session system. To ensure further security, the session ID should only be shared through signed and confidential communication channels.

### 3. Session Data Storage

The middleware provides functionality for storing session data. This allows you to conveniently store and retrieve data specific to each user session.

### 4. Session Cookie Management

The Session Middleware handles session cookie management, including signature verification. This ensures that the session cookies are tamper-proof and enhances the overall security of the session system.

### 5. In-Memory Store

The middleware supports an in-memory store for session data. This enables efficient storage and retrieval of session-related information.

By leveraging the Session Middleware, you can easily implement a robust and secure session management system in your FastAPI applications.

## Usage

Here is a basic usage example:

```python
from fastapi import FastAPI, Request

from authx._internal import MemoryIO
from authx.external import SessionMiddleware

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="my-secret-key",
    store=MemoryIO(),
    http_only=True,
    secure=False,
    max_age=0,
    session_cookie="sid",
    session_object="session",
)


@app.get("/session_test")
async def session(request: Request):
    session_manager = request.state.session
    session = session_manager.get_session()
    session_id = session_manager.get_session_id()

    print(f"sessionID:{session_id}")

    if "test_counter" not in session:
        session["test_counter"] = 0

    session["test_counter"] += 1

    return {"test_counter": session['test_counter']}
```

It provides functionality for storing and retrieving session data during HTTP requests.

Attributes:

- `secret_key`: A secret key used for session encryption and decryption.
- `store`: An optional parameter specifying the session storage. By default, it uses a `MemoryIO` store, but you can provide your own custom session store implementation.
- `http_only`: A boolean indicating whether the session cookie should be accessible only through HTTP requests (default is `True`).
- `secure`: A boolean indicating whether the session cookie should only be transmitted over HTTPS (default is `True`).
- `max_age`: The maximum age of the session cookie in seconds. If set to 0 (default), the cookie will expire at the end of the browser session.
- `session_cookie`: The name of the session cookie (default is "sid").
- `session_object`: The name of the attribute that will be added to the request scope to access the session object (default is "session").
- `skip_session_header`: An optional header name that, if present in the request, will skip the session handling for that particular request.
- `logger`: An optional logger instance for logging session-related events.
