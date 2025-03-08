# AuthX Examples

Simple examples showing how to use AuthX with FastAPI for authentication and authorization.

## Installation

```bash
uv sync
```

## Available Examples

1. **Basic Authentication** (`basic_auth_example.py`)
   - JWT token authentication
   - Protected routes

2. **Refresh Tokens** (`refresh_token_example.py`)
   - Access and refresh token handling
   - Token refresh flow

3. **Token Blocklist** (`token_blocklist_example.py`)
   - Token revocation
   - Logout functionality

4. **Token Locations** (`token_locations_example.py`)
   - Authorization headers
   - Cookies
   - Request body
   - Query parameters

5. **Fresh Tokens** (`fresh_token_example.py`)
   - Fresh vs non-fresh tokens
   - Sensitive operations protection

## Running Examples

1. Start an example:

   ```bash
   python example_name.py
   ```

2. Access the API docs:
   - Open <http://localhost:8000/docs>
   - Test endpoints through the interactive UI

## Note

These examples are for demonstration purposes. For production use:

- Use environment variables for secrets
- Enable HTTPS
- Implement proper database storage

For more details, visit [AuthX Documentation](https://authx.yezz.me/)
