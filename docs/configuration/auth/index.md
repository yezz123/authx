# Authentication

**AuthX** allows you to plug in several authentication methods.

## How it works?

You can have **multiple** authentication methods, e.g. a cookies authentication for browser-based queries and Token-based authentication with JWT for pure API queries.

When checking the authentication, each method runs one after the other. The first method yielding a user wins. If no method yields a user, an `HTTPException` is raised.

For each backend, you'll be able to add a router with the corresponding `/login` and `/logout` (if applicable routes). More on this in the Router section.

## Provided methods

* [JWT authentication](jwt.md)
* Cookie authentication (Under Development)
