# JWT Locations

JWT can be provided with requests in different locations. AuthX allows you to control and configure the JWT locations via the `JWT_TOKEN_LOCATION` setting.

```python
from fastapi import FastAPI, Depends
from authx import AuthX, AuthXConfig

app = FastAPI()

config = AuthXConfig()
config.JWT_TOKEN_LOCATION = ["headers", "query", "cookies", "json"]

security = AuthX(config=config)

@app.get('/protected', dependencies=[Depends(security.access_token_required)])
def protected():
    return "OK"
```

## Headers

JWT via headers is controlled by two settings:

- `JWT_HEADER_NAME`: The header name. By default, it's `'Authorization'`.
- `JWT_HEADER_TYPE`: The header value type/prefix. By default, it's `'Bearer'`.

The AuthX instance will check this specific header whenever it needs to retrieve a token if the `"headers"` location is in `JWT_TOKEN_LOCATION`.

Authentication is based solely on the presence of the `JWT_HEADER_NAME` header in the headers. To log out your user, remove the authorization header.

=== "cURL"

     ```shell
     $ curl --oauth2-bearer $TOKEN http://0.0.0.0:8000/protected
     "OK"
     # OR
     $ curl -H 'Authorization: "Bearer $TOKEN"' http://0.0.0.0:8000/protected
     ```
=== "JavaScript"

     ```js
     async function requestProtectedRoute(TOKEN){
     const response = await fetch("http://0.0.0.0:8000/protected", {
          method: "GET",
          headers: {
               "Authorization": `Bearer ${TOKEN}`
          }
     })
     return response
     }
     ```
=== "Python"

     ```python
     import requests

     r = request.get(
     "http://0.0.0.0:8000/protected",
     headers={
          "Authorization": f"Bearer {TOKEN}"
     }
     )
     ```

## Query Parameters

JWT via query parameters is controlled by a single setting:

- `JWT_QUERY_STRING_NAME`: The key used in the query string to identify the token. By default, it's `'token'`.

It's important to note that using JWT in query strings is not advised. Even with HTTPS protocol, the request URL is not protected, hence the token is visible. Such requests will be saved in plain text in browsers and could be easily compromised.

JWTs in query strings can be used by suffixing the URL with `?token=$TOKEN`.

=== "cURL"

     ```shell
     $ curl http://0.0.0.0:8000/protected?token=$TOKEN
     "OK"
     ```
=== "JavaScript"

     ```js
     async function requestProtectedRoute(TOKEN){
     const response = await fetch(`http://0.0.0.0:8000/protected?token=${TOKEN}`)
     return response
     }
     ```
=== "Python"

     ```python
     import requests

     r = request.get(f"http://0.0.0.0:8000/protected?token={TOKEN}")
     ```

## JSON Body

JWT via JSON Body is controlled by the following parameters:

- `JWT_JSON_KEY`: The JSON key relative to the access token. By default, it's `'access_token'`.
- `JWT_REFRESH_JSON_KEY`: The JSON key relative to the refresh token. By default, it's `'refresh_token'`.

Sending JWT via JSON Body cannot be accomplished with GET requests and requires the `Content-Type: application/json` header.

=== "cURL"

     ```shell
     curl -X POST -s --json '{"access_token":"$TOKEN"}' http://0.0.0.0:8000/protected
     "OK"
     ```
=== "JavaScript"

     ```js
     async function requestProtectedRoute(TOKEN){
     const response = await fetch("http://0.0.0.0:8000/protected", {
          method: "POST",
          headers: {
               "Content-Type": "application/json"
          },
          body: JSON.stringify({
               "access_token": TOKEN
          })
     })
     return response
     }
     ```
=== "Python"

     ```python
     import requests

     r = request.post(
     "http://0.0.0.0:8000/protected",
     json={
          "access_token": TOKEN
     }
     )
     ```

## Cookies

JWT via Cookies is controlled by various parameters:

- `JWT_ACCESS_COOKIE_NAME`: Cookie name containing the access token. By default, it's `access_token_cookie`.
- `JWT_ACCESS_COOKIE_PATH`: Path of the access token cookie. By default, it's `/`.
- `JWT_COOKIE_CSRF_PROTECT`: Enable CSRF protection for cookie authentication. By default, it's `True`.
- `JWT_COOKIE_DOMAIN`: The domain for cookies set by AuthX. By default, it's `None`.
- `JWT_COOKIE_MAX_AGE`: Max age for cookies set by AuthX. By default, it's `None`.
- `JWT_COOKIE_SAMESITE`: The SameSite property for cookies set by AuthX. By default, it's `Lax`.
- `JWT_COOKIE_SECURE`: Enable Cookie Secure property. By default, it's `True`.
- `JWT_REFRESH_COOKIE_NAME`: Cookie name containing the refresh token. By default, it's `refresh_token_cookie`.
- `JWT_REFRESH_COOKIE_PATH`: Path of the refresh token cookie. By default, it's `/`.
- `JWT_ACCESS_CSRF_COOKIE_NAME`: Cookie name containing the access CSRF token. By default, it's `csrf_access_token`.
- `JWT_ACCESS_CSRF_COOKIE_PATH`: Path of the access CSRF token cookie. By default, it's `/`.
- `JWT_CSRF_IN_COOKIES`: Add CSRF tokens when cookies are set by AuthX. By default, it's `True`.
- `JWT_REFRESH_CSRF_COOKIE_NAME`: Cookie name containing the refresh CSRF token. By default, it's `csrf_refresh_cookie`.
- `JWT_REFRESH_CSRF_COOKIE_PATH`: Path of the refresh CSRF token cookie. By default, it's `/`.

Using JWTs in cookies is suitable for web application authentication, but it requires additional work to prevent attacks, such as Cross-Site Request Forgery (CSRF).

=== "cURL"

     ```shell
     curl -X POST -s --cookie "access_token_cookie=$TOKEN" -H 'X-CSRF-TOKEN: "$CSRF_TOKEN"' http://0.0.0.0:8000/protected
     "OK"
     ```
=== "JavaScript"

     ```js
     function getCookie(cname) {
     const name = cname + "=";
     const decodedCookie = decodeURIComponent(document.cookie);
     const cookieArray = decodedCookie.split(';');

     for (let i = 0; i < cookieArray.length; i++) {
          let cookie = cookieArray[i];
          while (cookie.charAt(0) === ' ') {
               cookie = cookie.substring(1);
          }
          if (cookie.indexOf(name) === 0) {
               return cookie.substring(name.length, cookie.length);
          }
     }
     return "";
     }

     // Function to get CSRF token from cookie
     function getCSRFCookie() {
     return getCookie("csrf_access_token");
     }

     // Function to make a request to a protected route
     async function requestProtectedRoute() {
     const csrfToken = getCSRFCookie();
     const requestOptions = {
          method: "POST",
          credentials: 'include',
          headers: {
               "Content-Type": "application/json", // Assuming you're sending JSON data
               "X-CSRF-TOKEN": csrfToken
          }
     };

     try {
          const response = await fetch("http://0.0.0.0:8000/protected", requestOptions);
          return response;
     } catch (error) {
          console.error("Error occurred while making the request:", error);
          throw error;
     }
     }

     ```
=== "Python"

     ```python
     import requests

     r = request.post(
     "http://0.0.0.0:8000/protected",
     headers= {
          "X-CSRF-TOKEN": CSRF_TOKEN
     },
     cookies={
          "access_token_cookie": TOKEN,
     }
     )
     ```
