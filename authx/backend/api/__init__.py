from authx.backend.api.confirm import UsersConfirmMixin
from authx.backend.api.crud import UsersCRUDMixin
from authx.backend.api.manage import UsersManagementMixin
from authx.backend.api.password import UsersPasswordMixin
from authx.backend.api.protection import UsersProtectionMixin
from authx.backend.api.users import UsersUsernameMixin


class UsersRepo(
    UsersCRUDMixin,
    UsersConfirmMixin,
    UsersPasswordMixin,
    UsersUsernameMixin,
    UsersProtectionMixin,
    UsersManagementMixin,
):
    """User Repository"""
