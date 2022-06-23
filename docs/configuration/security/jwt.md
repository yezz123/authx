# Json Web Token

Json Web Token is a security feature that is used to protect your application,
and it is very important to have a good security configuration.

Authx Provide a full configuration for Json Web Token, and you can use it to
protect your application, with a lot of features that coded natively in AuthX
like supporting redis cache and more.

You can Easily extend on it based on a pre Coded Class `JWTBackend` thats
depends on:

- Cache Backend: Which you can use Redis Cache Backend, or you can use a Cache
  Backend that you have implemented.
- Private Key: Which you can use a Private Key that you have generated, or you
  can use a Private Key that you have generated.
- Public Key: Which you can use a Public Key that you have generated, or you can
  use a Public Key that you have generated.
- Access Token Expiration: Which you can use a Access Token Expiration that you
  have generated, or you can use a Access Token Expiration that you have
  generated.
- Refresh Token Expiration: Which you can use a Refresh Token Expiration that
  you have generated, or you can use a Refresh Token Expiration that you have
  generated.

You could use the following configuration to generate and Extend on the
`JWTBackend`:

```py
from authx import JWTBackend, RedisCacheBackend

SecurityConfig = JWTBackend(
    cache_backend=RedisCacheBackend(host='localhost', port=6379),
    private_key=("private_key"),
    public_key=("public_key"),
    access_token_expiration=3600,
    refresh_token_expiration=3600
)
```

In this way we could use Features like Decode token and Create Token also
`create_access_token` and `create_refresh_token` and Admin Features like
`active_blackout` or `user_logout` or `user_in_Blacklist`.

As i Said you could extend on others features that depend the Security using JWT
and use it in your application based on the configuration.
