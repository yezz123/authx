# Social Authentication

the Main Class `SocialService` is the main class that is used to perform all Social Authentication operations.

```py
from authx import SocialService, UsersRepo, JWTBackend


Service = SocialService(
    repo = UsersRepo(),
    auth_backend= JWTBackend(),
    base_url = 'http://localhost:5000',
)
```
