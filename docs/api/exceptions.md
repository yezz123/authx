# AuthXException

::: authx.exceptions.AuthXException

The base exception for all AuthX exceptions.

::: authx.exceptions.BadConfigurationError

Raised when AuthX configuration contains wrong parameters.

::: authx.exceptions.JWTDecodeError

Raised when decoding JSON Web Token fails.

::: authx.exceptions.NoAuthorizationError

Raised when no token can be parsed from request.

::: authx.exceptions.CSRFError

Raised when CSRF protection failed.

::: authx.exceptions.TokenError

Raised when token is invalid.

::: authx.exceptions.MissingTokenError

Raised when no token can be parsed from request.

::: authx.exceptions.MissingCSRFTokenError

Raised when no CSRF token can be parsed from request.

::: authx.exceptions.TokenTypeError

Raised when token type is invalid.

::: authx.exceptions.RevokedTokenError

Raised when token is invalid.

::: authx.exceptions.TokenRequiredError

Raised when token is required.

::: authx.exceptions.FreshTokenRequiredError

Raised when fresh token is required.

::: authx.exceptions.AccessTokenRequiredError

Raised when access token is required.

::: authx.exceptions.RefreshTokenRequiredError

Raised when refresh token is required.

::: authx.exceptions.InvalidToken

     Raised when token is invalid.
