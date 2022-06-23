## Models

**AuthX** defines a minimal User model for authentication purposes. It is
structured like this:

- `id` (`int`) – Unique identifier of the user. Defaults to a **Int**.
- `email` (`str`) – Email of the user. Validated by
  [`email-validator`](https://github.com/JoshData/python-email-validator).
- `active` (`bool`) – Whether or not the user is active. If not, login and
  forgot password requests will be denied. Defaults to `True`.
- `confirmed` (`bool`) – Whether or not the user is verified. Optional but
  helpful with the `verify` router logic. Defaults to `False`.
- `permissions` (`bool`) – Whether or not the user is a superuser. Useful to
  implement administration logic. Defaults to `False`.
- `last_login` (`datetime`) – When the user last logged in. Defaults to `None`.
- `created_at` (`datetime`) – When the user was created. Defaults to `None`.

There is also a Social User model that is a class of the AuthX User model.

- `provider` (`str`) – The provider of the social user.
- `sid` (`str`) – The unique identifier of the social user.
- `active` (`bool`) – Whether or not the social user is active. Defaults to
  `True`.
- `confirmed` (`bool`) – Not like Base Case,but when a user logs in with a
  social user, the social user is confirmed. Defaults to `True`.

## Get Started

Start using the defined models in your application, by reading:

- [Base Models](base.md)
- [Social Models](social.md)
- [Project Properties](properties.md)
