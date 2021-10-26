# UserManager

The UserManager class is the core logic of AuthX. We provide the `UsersRepo` class which you should extend to set some parameters and define logic, for example when a user just registered or forgot its password.

It's designed to be easily extensible and customizable so that you can integrate less generic logic.

The `UsersRepo` is a general class with multiple classes, that allow us to perform the following actions:

### Base

* `Base`: Where we initialize the UserManager, using some parameters.
    * `Database`: The database connection.
    * `cache`: The cache connection.
    * `callbacks`: The callbacks to be executed when a user is created or updated.
    * `access_expiration`: The time in seconds that a token is valid.

### UsersCRUDMixin

* `UsersCRUDMixin`: This class is responsible for the CRUD operations on users.
    * `get`: Get a user by its id.
    * `get_by_email`: Get a user by its email.
    * `get_by_username`: Get a user by its username.
    * `get_by_social`: Get a user by its social using provider and social ID.
    * `get_by_login`: Get a user by its login.
    * `create`: Create a user take as parameters the `obj`.
    * `update`: Update a user take as parameters the `id` and `obj`.
    * `delete`: Delete a user take as parameters the `id`.
    * `update_last_login`: Update the last login of a user.
    * `search`: Search users by a query.

### UsersProtectionMixin

* `UsersProtectionMixin`: Create all the Common Protection GET, POST, PUT, DELETE methods.
    * `_check_timeout_and_incr`: Check if the token is valid and increment the access counter.
    * `is_bruteforce`: Check if the user is in a bruteforce attack, based on `IP` , and Login.

### UsersConfirmMixin

* `UsersConfirmMixin`: Create all the Common Confirm GET, POST, PUT, DELETE methods.
    * `is_email_confirmation_available`: Check if the email confirmation is available.
    * `request_email_confirmation`: Request a new email confirmation.
    * `confirm_email`: Confirm an email based on the `token`.

### UsersUsernameMixin

* `UsersUsernameMixin`: Create all the Common Username GET, POST, PUT, DELETE methods.
    * `change_username`: Change the username of a user, based on the `id` and `new_username`.

### UsersPasswordMixin

* `UsersPasswordMixin`: Create all the Common Password GET, POST, PUT, DELETE methods.
    * `get_password_status`: Get the password status of a user, based on the `id`.
    * `set_password`: Set the password of a user, based on the `id` and `password`.
    * `is_password_reset_available`: Check if the password reset is available.
    * `set_password_reset_token`: Set the password reset token of a user, based on the `id` and `token`.
    * `get_id_for_password_reset`: Get the id for password reset, based on the `token`.

### UsersManagementMixin

* `UsersManagementMixin`: Create all the Common Management GET, POST, PUT, DELETE methods.
    * `get_blacklist`: Get the blacklist of a user.
    * `toggle_blacklist`: Toggle the blacklist of a user, based on the `id`.
    * `kick`: Kick a user, based on the `id`.
    * `get_blackout`: Get the blackout of a user.
    * `set_blackout`: Set the blackout of a user, based on the `ts`.
    * `delete_blackout`: Delete the blackout of a user.
    * `set_permissions`: Set the permissions of a user.

!!! warning
    This one relate to the Admin route, and is not available in the User route too.
