# Facebook OAuth

Facebook uses OAuth2 for its auth process. Further documentation at [Facebook development resources](https://developers.facebook.com/docs/facebook-login):

- Register a new application at [Facebook App Creation](https://developers.facebook.com/apps/), don’t use localhost as App Domains and Site URL since Facebook won’t allow them. Use a placeholder like `app.com` and define that domain in your `/etc/hosts` or similar file.

Login to facebook, use some parameters:

* `client_id`: The App ID you got from Facebook
* `redirect_uri`: The URL to redirect to after authentication
* `client_secret`: The App Secret you got from Facebook
* `scope`: The permissions you want to request

## Login with Facebook

We have this function to login with Facebook.

```py
def login_facebook(self, state: str) -> str:
        redirect_uri = self._create_redirect_uri("facebook")
        return f"https://www.facebook.com/v8.0/dialog/oauth?client_id="
```

The `_create_redirect_uri` function is used to create the redirect URI, based on `base_url` a string and the `provider` a string.

__Note:__ The `client_id` here we define the parameters for the OAuth2 process.

## Facebook Response

After, the user is redirected to the `redirect_uri` and the `code` is passed to the `/oauth/access_token` endpoint.

```py
access_token = response.json().get("access_token")
response = await client.get("https://graph.facebook.com/me",
    params={"access_token": access_token, "fields": "id,email"},)
```

Here we use the `access_token` to get the user’s data, and add it to the database, also confirm the user’s email.

I guess we have the Same logic for the other providers, but with different endpoints & Params.

## Check Also

* [Google](google.md)
* [Addons](addons.md)
