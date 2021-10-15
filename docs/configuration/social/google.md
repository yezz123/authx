# Google Oauth2

Recently Google launched OAuth2 support following the definition at OAuth2 draft. It works in a similar way to plain OAuth mechanism, but developers __must__ register an application and apply for a set of keys. Check [Google OAuth2](http://code.google.com/apis/accounts/docs/OAuth2.html) document for details.

When creating the application in the Google Console be sure to fill the `PRODUCT NAME` at `API` & `auth` -> Consent `screen` form.

Close to Facebook Logic, Google use also some parameters to identify the application.

* `code`: Generated code from the `redirect_uri`
* `client_id`: The client ID of the application
* `client_secret`: The client secret of the application
* `redirect_uri`: The redirect URI of the application
* `grant_type`: The grant type of the application

## Login with Google

We have this function to login with Google.

```py
def login_google(self, state: str) -> str:
        redirect_uri = self._create_redirect_uri("google")
        return f"https://accounts.google.com/o/oauth2/v2/auth?scope="
```

The `_create_redirect_uri` function is used to create the redirect URI, based on `base_url` a string and the `provider` a string.

__Note:__ The `scope` here we define the parameters for the OAuth2 process.

## Google Response

After, the user is redirected to the `redirect_uri` and the `code` is passed to the server.

```py
data = response.json()
id_token = data.get("id_token")
payload = jwt.decode(id_token, verify=False)
sid = payload.get("sub")
email = payload.get("email")
```

Here we use the `jwt` library to decode the `id_token` and get the `sub` and `email` from the payload.

I guess we have the Same logic for the other providers, but with different endpoints & Params.

## Check Also

* [Addons](addons.md)
