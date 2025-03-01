# AuthX Examples

This directory contains several examples demonstrating how to use AuthX with FastAPI for authentication and authorization.

## Prerequisites

Before running these examples, make sure you have installed AuthX:

```bash
uv add authx
```

## Examples Overview

### 1. Basic Authentication Example (`basic_auth_example.py`)

A simple example demonstrating basic authentication with JWT tokens.

**Features demonstrated:**

- Configuring AuthX
- User login with JWT token generation
- Protected routes requiring authentication
- Token verification

**To run:**

```bash
python basic_auth_example.py
```

### 2. Refresh Token Example (`refresh_token_example.py`)

Demonstrates how to use refresh tokens to obtain new access tokens without requiring the user to log in again.

**Features demonstrated:**

- Access token and refresh token generation
- Using refresh tokens to get new access tokens
- Token expiration configuration

**To run:**

```bash
python refresh_token_example.py
```

### 3. Token Blocklist Example (`token_blocklist_example.py`)

Shows how to implement a token blocklist (revocation) system to invalidate tokens before they expire.

**Features demonstrated:**

- Token blocklisting/revocation
- Custom blocklist callback
- Logout functionality

**To run:**

```bash
python token_blocklist_example.py
```

### 4. Token Locations Example (`token_locations_example.py`)

Demonstrates the different ways tokens can be provided in requests.

**Features demonstrated:**

- Configuring multiple token locations
- Accepting tokens in:
  - Authorization headers
  - Cookies (with CSRF protection)
  - JSON request body
  - Query parameters
- Setting and unsetting cookies

**To run:**

```bash
python token_locations_example.py
```

### 5. Fresh Token Example (`fresh_token_example.py`)

Shows how to use fresh tokens for sensitive operations.

**Features demonstrated:**

- Fresh vs non-fresh tokens
- Requiring fresh tokens for sensitive operations
- Converting refresh tokens to non-fresh access tokens

**To run:**

```bash
python fresh_token_example.py
```

## Testing the Examples

After starting any of the examples, you can interact with them using tools like:

1. **curl** from the command line
2. **Postman** or similar API testing tools
3. **FastAPI's automatic documentation** at http://localhost:8000/docs

## Example Workflow

Here's a typical workflow for testing these examples:

1. Start the example server: `python example_name.py`
2. Access the documentation at http://localhost:8000/docs
3. Use the `/login` endpoint to get tokens
4. Use the tokens to access protected endpoints
5. Try different token locations or features depending on the example

## Security Notes

These examples are for demonstration purposes only and include simplified security practices:

- Secret keys are hardcoded (in production, use environment variables)
- HTTPS is not enforced (in production, always use HTTPS)
- User data is stored in memory (in production, use a proper database)

## Additional Resources

- [AuthX Documentation](https://authx.yezz.me/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JWT.io](https://jwt.io/) - Useful for inspecting JWT tokens
