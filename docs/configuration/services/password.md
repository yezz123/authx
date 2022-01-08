# Password

the Main Class `PasswordService` is the main class that is used to perform all password operations.

```py
from authx import PasswordService, UsersRepo, JWTBackend


Service = PasswordService(
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
