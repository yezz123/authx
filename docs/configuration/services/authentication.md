# Authentication

Using the Service and Crud Operations thats coded in Authx natively thats could be used with different routers.

the Main Class `AuthService` is the main class that is used to authenticate users.

```py
from authx import AuthService, UsersRepo, JWTBackend


Service = AuthService(
    repo = UsersRepo,
    auth_backend= JWTBackend,
    debug = True,
    base_url = 'http://localhost:5000',
    site = 'http://localhost:5000',
    recaptcha_secret = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
    smtp_username = 'username',
    smtp_password = 'password',
    smtp_host = 'smtp.gmail.com',
    smtp_tls = True,
    display_name = 'AuthX',
)
```
