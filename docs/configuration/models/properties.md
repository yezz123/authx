## Properties

There is a file `common.py` that contains the common properties for all models.

`set_created_at` (`bool`) – Return the created_at property as a datetime object.

`set_last_login` (`bool`) – Return the last_login property as a datetime object.

Also a class `DefaultModel` that can be used to define a default model, with a
configuration that allow:

- `allow_population_by_field_name` – Allow population by field name. default:
  `True`.
- `alias_generator` – this one based on a Function, called
  `convert_field_to_camel_case` that converts a field name to a camel case.
  default: `None`.

Check the
[pydantic documentation](https://pydantic-docs.helpmanual.io/usage/models/) for
more information.

Check also:

- [Base Models](base.md)
- [Social Models](social.md)
