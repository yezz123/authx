# Social Models

## Define your Social Models

There are one Pydantic model variation provided as mixin:

* `SocialInCreate` – Social User model for creating.

You should define it, inheriting from the mixin:

```py
from AuthX.models import social

class Create(social.SocialInCreate):
    pass

class login(social.SocialInCreate):
    pass
```

!!! warning
    Take Care! you can't add any field to the model, because it's relate to the third party of the Provider (ex. Facebook, Google, etc.)

Check the [pydantic documentation](https://pydantic-docs.helpmanual.io/usage/models/) for more information.

Check also:

* [Base Models](base.md)
* [properties](properties.md)
